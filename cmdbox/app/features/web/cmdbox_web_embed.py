from cmdbox.app import feature, common
from cmdbox.app.web import Web
from cmdbox.app.commons import convert
from cmdbox.app.features.cli import (
    cmdbox_embed_list,
    cmdbox_embed_embedding,
    cmdbox_embed_start,
)
from fastapi import FastAPI, Request, Response, HTTPException
import argparse
import time


class Embed(feature.WebFeature):
    
    def route(self, web: Web, app: FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        self.embed_list = cmdbox_embed_list.EmbedList(self.appcls, self.ver, self.language)
        self.embed_embedding = cmdbox_embed_embedding.EmbedEmbedding(self.appcls, self.ver, self.language)
        self.embed_start = cmdbox_embed_start.EmbedStart(self.appcls, self.ver, self.language)

        @app.post('/v1/embeddings')
        async def embeddings_endpoint(req: Request, res: Response):
            """
            OpenAI互換のembeddings APIエンドポイント
            
            リクエスト形式:
            {
                "input": "テキスト" または ["テキスト1", "テキスト2"],
                "model": "embed_name",
                "encoding_format": "float" (オプション)
            }
            
            レスポンス形式:
            {
                "object": "list",
                "data": [
                    {
                        "object": "embedding",
                        "index": 0,
                        "embedding": [0.123, 0.456, ...]
                    }
                ],
                "model": "embed_name",
                "usage": {
                    "prompt_tokens": 10,
                    "total_tokens": 10
                }
            }
            """
            # リクエストボディを取得
            body = await req.json()
            
            # バリデーション
            if 'input' not in body:
                raise HTTPException(status_code=400, detail="'input' field is required")
            
            if 'model' not in body:
                raise HTTPException(status_code=400, detail="'model' field is required")
            
            input_data = body.get('input')
            model = body.get('model')
            encoding_format = body.get('encoding_format', 'float')
            
            # inputをリストに正規化
            if isinstance(input_data, str):
                inputs = [input_data]
            elif isinstance(input_data, list):
                inputs = input_data
            else:
                raise HTTPException(status_code=400, detail="'input' must be a string or list of strings")
            
            # サポートモデルを取得
            args = argparse.Namespace(
                host=web.redis_host,
                port=web.redis_port,
                password=web.redis_password,
                svname=web.svname,
                retry_count=3,
                retry_interval=5,
                timeout=60,
                kwd='*',
                format=False,
                output_json=None,
                output_json_append=False
            )
            st, list_res, _ = self.embed_list.apprun(web.logger, args, 0, [])
            if st != self.embed_list.RESP_SUCCESS or 'success' not in list_res:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to retrieve supported models: {common.to_str(list_res)}"
                )
            supported_models = [m['name'] for m in list_res['success']]
            if model not in supported_models:
                raise HTTPException(
                    status_code=400,
                    detail=f"Model '{model}' is not supported. Supported models: {', '.join(supported_models)}"
                )

            # モデルを起動
            args.embed_name = model
            st, start_res, _ = self.embed_start.apprun(web.logger, args, 0, [])
            if st != self.embed_start.RESP_SUCCESS or 'success' not in start_res:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to start embedding model '{model}': {common.to_str(start_res)}"
                )
            
            # embeddingを生成（cmdbox_embed_embedding._embedding を使用）
            args.original_data = inputs
            st, embed_res, _ = self.embed_embedding.apprun(web.logger, args, 0, [])
            if st != self.embed_embedding.RESP_SUCCESS or 'success' not in embed_res:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate embeddings: {common.to_str(embed_res)}"
                )

            # embeddings_dataを構築
            embeddings_data = []
            list_data = embed_res.get('success', [])
            for index, item in enumerate(list_data):
                b64embed = item.get('embed')
                
                # encoding_formatに応じた形式に変換
                if encoding_format == 'base64':
                    embeddings_data.append(dict(
                        object="embedding",
                        index=index,
                        embedding=b64embed
                    ))
                else:
                    embed_array = convert.b64str2npy(b64embed, item.get('shape'), item.get('type'))
                    embedding = embed_array.tolist()
                    embeddings_data.append(dict(
                        object="embedding",
                        index=index,
                        embedding=embedding
                    ))

            # トークン数を推定（文字数 / 4 がおおよその目安）
            total_tokens = sum(len(text) // 4 + 1 for text in inputs)

            # レスポンスを構築
            response_data = dict(
                object="list",
                data=embeddings_data,
                model=model,
                usage=dict(
                    prompt_tokens=total_tokens,
                    total_tokens=total_tokens
                )
            )
            return response_data
        
        @app.get('/v1/models')
        async def models_endpoint(req: Request, res: Response):
            """
            利用可能なモデル一覧を返す（OpenAI互換）
            """
            # サポートモデルを取得
            args = argparse.Namespace(
                host=web.redis_host,
                port=web.redis_port,
                password=web.redis_password,
                svname=web.svname,
                retry_count=3,
                retry_interval=5,
                timeout=60,
                kwd='*',
                format=False,
                output_json=None,
                output_json_append=False
            )
            st, list_res, _ = self.embed_list.apprun(web.logger, args, 0, [])
            if st != self.embed_list.RESP_SUCCESS or 'success' not in list_res:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to retrieve supported models: {common.to_str(list_res)}"
                )
            supported_models = [dict(id=m['name'], object="model", created=int(time.time()), owned_by="cmdbox")
                                for m in list_res['success']]
            return dict(object="list", data=supported_models)
