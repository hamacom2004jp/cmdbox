docker-entrypoint.sh
sudo -u postgres postgres -c shared_preload_libraries="pg_cron,pg_stat_statements" -c cron.database_name="pgsql"
