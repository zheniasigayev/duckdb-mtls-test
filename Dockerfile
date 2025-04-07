FROM nginx:alpine
COPY certs/server.crt /etc/nginx/certs/server.crt
COPY certs/server.key /etc/nginx/certs/server.key
COPY certs/ca.crt /etc/nginx/certs/ca.crt
COPY nginx-config/default.conf /etc/nginx/conf.d/default.conf
COPY data/data.parquet /usr/share/nginx/html/data.parquet

# Expose HTTPS port
EXPOSE 443