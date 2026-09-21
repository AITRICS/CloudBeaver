FROM dbeaver/cloudbeaver:26.2.0

ARG CLOUDBEAVER_VERSION=26.2.0
ARG BUILD_REVISION=r1

LABEL org.opencontainers.image.title="CloudBeaver" \
      org.opencontainers.image.description="CloudBeaver with pinned offline Oracle, MySQL and SQL Server JDBC profiles" \
      org.opencontainers.image.version="26.2.0-r1" \
      org.opencontainers.image.source="https://github.com/dbeaver/cloudbeaver"

USER root

COPY build/output/ /opt/cloudbeaver/server/plugins/

RUN keytool -genkeypair -alias cloudbeaver-custom \
        -keystore /tmp/cloudbeaver-custom.p12 -storetype PKCS12 \
        -storepass changeit -keypass changeit \
        -dname "CN=CloudBeaver Offline Build" \
        -keyalg RSA -keysize 3072 -validity 3650 -noprompt \
    && for plugin in \
        /opt/cloudbeaver/server/plugins/org.jkiss.dbeaver.ext.oracle_*.jar \
        /opt/cloudbeaver/server/plugins/org.jkiss.dbeaver.ext.mssql_*.jar \
        /opt/cloudbeaver/server/plugins/io.cloudbeaver.resources.drivers.base_*.jar; do \
         jarsigner -keystore /tmp/cloudbeaver-custom.p12 -storetype PKCS12 \
             -storepass changeit -keypass changeit "$plugin" cloudbeaver-custom; \
       done \
    && rm -f /tmp/cloudbeaver-custom.p12

RUN rm -f /opt/cloudbeaver/drivers/mysql/mysql8/mysql-connector-j-*.jar \
    && rm -f /opt/cloudbeaver/drivers/mssql/new/mssql-jdbc-*.jar \
    && mkdir -p \
       /opt/cloudbeaver/drivers/oracle/modern \
       /opt/cloudbeaver/drivers/oracle/compat \
       /opt/cloudbeaver/drivers/oracle/legacy \
       /opt/cloudbeaver/drivers/mssql/legacy

COPY drivers/oracle/modern/ /opt/cloudbeaver/drivers/oracle/modern/
COPY drivers/oracle/compat/ /opt/cloudbeaver/drivers/oracle/compat/
COPY drivers/oracle/legacy/ /opt/cloudbeaver/drivers/oracle/legacy/
COPY drivers/mysql/mysql-connector-j-8.4.0.jar /opt/cloudbeaver/drivers/mysql/mysql8/
COPY drivers/mssql/modern/mssql-jdbc-13.6.0.jre11.jar /opt/cloudbeaver/drivers/mssql/new/
COPY drivers/mssql/legacy/ /opt/cloudbeaver/drivers/mssql/legacy/

RUN find /opt/cloudbeaver/drivers/oracle/modern \
            /opt/cloudbeaver/drivers/oracle/compat \
            /opt/cloudbeaver/drivers/oracle/legacy \
            /opt/cloudbeaver/drivers/mysql/mysql8 \
            /opt/cloudbeaver/drivers/mssql/new \
            /opt/cloudbeaver/drivers/mssql/legacy \
            -type f -name '*.jar' -exec chmod 0644 {} +
