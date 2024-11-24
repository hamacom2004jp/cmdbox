.. -*- coding: utf-8 -*-

****************
開発者向け情報
****************

cmdboxの開発環境を構築するための手順を説明します。

プロジェクトのインストール方法
==============================

プロジェクトをインストールするには、次の手順を実行します:

1. プロジェクトをクローンします:

    .. code-block:: bat

        git clone https://github.com/hamacom2004jp/cmdbox.git

2. プロジェクトのディレクトリに移動します:

    .. code-block:: bat

        cd cmdbox

3. プロジェクトの仮想環境を作成します:

    .. code-block:: bat

        python -m venv .venv
        .venv\Scripts\activate

4. プロジェクトの依存関係をインストールします:

    .. code-block:: bat

        python.exe -m pip install --upgrade pip
        pip install -r requirements.txt

5. プロジェクトをビルドします:

    .. code-block:: bat

        sphinx-apidoc -F -o docs_src/resources cmdbox
        sphinx-build -b html docs_src docs
        python -m collectlicense --out cmdbox/licenses --clear
        python setup.py sdist
        python setup.py bdist_wheel

.. sphinx-build -b gettext docs_src docs_build
.. sphinx-intl update -p docs_build -l en
        
モジュールのコミット方法
=========================

開発を協力いただける方は、以下のガイドラインに従ってください:

1. 新しいブランチを作成してください:

    .. code-block:: bat

        git checkout -b feature/your-feature

2. 変更を加えてコミットしてください:

    .. code-block:: bat

        git commit -m "Add your changes"

3. 作成したブランチにプッシュしてください:

    .. code-block:: bat

        git push origin feature/your-feature

4. プルリクエストを作成してください.

【参考】pyplにアップするための手順
==================================

1. pypiのユーザー登録

   - pyplのユーザー登録【本番】
     https://pypi.org/account/register/

   - pyplのユーザー登録【テスト】
     https://test.pypi.org/account/register/

2. それぞれ2要素認証とAPIトークンを登録

3. ホームディレクトリに **.pypirc** を作成

    .. code-block:: ini

        [distutils]
        index-servers =
            pypi
            testpypi

        [pypi]
        repository: https://upload.pypi.org/legacy/
        username: __token__
        password: 本番環境のAPIトークン

        [testpypi]
        repository: https://test.pypi.org/legacy/
        username: __token__
        password: テスト環境のAPIトークン

4. テスト環境にアップロード

    .. code-block:: bat

        twine upload --repository testpypi dist/*

5. テスト環境のモジュールをインストール

    .. code-block:: bat

        pip install -i https://test.pypi.org/simple/ cmdbox

6. 本番環境にアップロード

    .. code-block:: bat

        twine upload --repository pypi dist/*

7. 本番環境のモジュールをインストール

    .. code-block:: bat

        pip install cmdbox

【参考】RedisをWindows環境を構築する手順
=====================================================

- `cmdbox` はRedisを使用しています。

    1. インストーラーを `GitHub <https://github.com/MicrosoftArchive/redis/releases>`__ からダウンロードします。
    2. ダウンロードしたインストーラー（MSIファイル）を実行します。
    3. ウィザードの中でインストール先ディレクトリの設定があるので、設定したパスをメモしておいてください。デフォルトは `C:\\Program Files\\Redis` です。
    4. ウィザードの中でRedisサーバーのサービスポートの設定があるので、設定したポートをメモしておいてください。デフォルトは6379です。
    5. ウィザードの中で使用するメモリ最大量の設定があるので、必要に応じて設定してください。開発用なら100mb程度で十分です。 
    6. インストールが完了したら、インストール先ディレクトリをエクスプローラーで開いてください。
    7. その中の `redis.windows-service.conf` ファイルと `redis.windows-service.conf` ファイルをメモ帳などのテキストエディタで開いてください。
    8. このファイルの中で、 `requirepass foobared` を検索し、 `#` を削除しコメントアウトを解除してください。
    9. `requirepass foobared` の `foobared` の部分を任意のパスワードに変更してください。変更したパスワードをメモしておいてください。
    10. このパスワードが、 `cmdbox` コマンドの中で指定するパスワードになります。
    11. Windowsのタスクマネージャーを開いて、サービスタブを開いて `Redis` を右クリックし、サービスを再起動してください。

【参考】sitemap.xmlの作成手順
=============================

1. `xml-sitemaps <https://www.xml-sitemaps.com/>`__ でsitemap.xmlを作成します。:
2. 作成したsitemap.xmlをダウンロードします。
3. ダウンロードしたsitemap.xmlを `docs` ディレクトリにコピーします。
4. プロジェクトのルートディレクトリに移動して、以下のコマンドを実行します:

    .. code-block:: bat

        sphinx-apidoc -F -o docs_src/resources cmdbox
        sphinx-build -b html docs_src docs
        python setup.py sdist
        python setup.py bdist_wheel

