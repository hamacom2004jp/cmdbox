if [[ "${CMDBOX_DEBUG}" = "true" ]]; then
    DEBUG="--debug"
else
    DEBUG=""
fi
cmdbox -m web -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME} \
       --listen_port ${LISTEN_PORT} --data /home/${MKUSER}/.cmdbox --allow_host 0.0.0.0 \
       --gunicorn_workers ${GUNICORN_WORKERS:-5} --gunicorn_timeout ${GUNICORN_TIMEOUT:-600} \
       --signin_file .cmdbox/user_list.yml ${DEBUG} &
cmdbox -m mcpsv -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME} \
       --mcpsv_listen_port ${MCPSV_LISTEN_PORT} --data /home/${MKUSER}/.cmdbox --allow_host 0.0.0.0 \
       --gunicorn_workers ${GUNICORN_WORKERS:-5} --gunicorn_timeout ${GUNICORN_TIMEOUT:-600} \
       --signin_file .cmdbox/user_list.yml ${DEBUG} &
cmdbox -m a2asv -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME} \
       --a2asv_listen_port ${A2ASV_LISTEN_PORT} --data /home/${MKUSER}/.cmdbox --allow_host 0.0.0.0 \
       --gunicorn_workers ${GUNICORN_WORKERS:-5} --gunicorn_timeout ${GUNICORN_TIMEOUT:-600} \
       --signin_file .cmdbox/user_list.yml ${DEBUG} &
if [[ -z "${SVCOUNT}" || "${SVCOUNT}" =~ ^[^0-9]+$ ]]; then
    echo "SVCOUNT is not a number. SVCOUNT=${SVCOUNT}"
    SVCOUNT=3
fi
for ((i=1; i<${SVCOUNT}; i++))
do
    cmdbox -m server -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME} --data /home/${MKUSER}/.cmdbox ${DEBUG} &
done
cmdbox -m server -c start --host ${REDIS_HOST} --port ${REDIS_PORT} --password ${REDIS_PASSWORD} --svname ${SVNAME} --data /home/${MKUSER}/.cmdbox ${DEBUG}
