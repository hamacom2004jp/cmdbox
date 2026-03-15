#{FROM}

ENV TZ=Asia/Tokyo
RUN apt-get update
RUN apt-get install -y build-essential git wget \
                       postgresql-server-dev-#{PGSQLVER} \
                       libkrb5-dev flex bison libreadline-dev zlib1g-dev cmake
#{INSTALL_PGVECTOR}
#{INSTALL_AGE}
#{INSTALL_PGCRON}

RUN echo "shared_preload_libraries = 'pg_cron,pg_stat_statements'" >> /usr/share/postgresql/postgresql.conf.sample
RUN apt-get purge -y --auto-remove build-essential git wget postgresql-server-dev-#{PGSQLVER} cmake
