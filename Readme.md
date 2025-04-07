# duckdb-mtls-test
This repository provides a reproducible setup for testing latency issues in DuckDB when querying a Parquet file over HTTPS with and without certificate verification. By following the steps below, you'll set up an NGINX server with a self-signed certificate, serve a Parquet file via Docker, and use the DuckDB CLI to measure query performance under different TLS verification settings.



### Step 0: Generate Certificates

Steps to Generate Certificates for mTLS
You can run these commands on your local machine or in a script to generate the certificates. Make sure you have OpenSSL installed (openssl command-line tool).

#### 0.1 - Generate the CA Certificate and Key
The CA will sign both the server and client certificates.

Generate CA private key
```bash
openssl genrsa -out ca.key 2048
```

Generate CA certificate (self-signed)
```bash
openssl req -x509 -new -nodes -key ca.key -sha256 -days 365 -out ca.crt -subj "/CN=MyCA"
```
ca.key: CA private key

ca.crt: CA certificate (public)

#### 0.2 - Generate the Server Certificate and Key
The server certificate will be signed by the CA.

Generate server private key

```bash
openssl genrsa -out server.key 2048
```

Generate server certificate signing request (CSR)
```bash
openssl req -new -key server.key -out server.csr -subj "/CN=localhost"
```

Sign the server CSR with the CA to create the server certificate
```bash
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256
```

Clean up the CSR
```bash
rm server.csr
```
server.key: Server private key

server.crt: Server certificate (signed by CA)

#### 0.3 - Generate the Client Certificate and Key

The client certificate will also be signed by the CA.

Generate client private key
```bash
openssl genrsa -out client.key 2048
```

Generate client certificate signing request (CSR)
```bash
openssl req -new -key client.key -out client.csr -subj "/CN=client"
```

Sign the client CSR with the CA to create the client certificate
```bash
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365 -sha256
```

Clean up the CSR
```bash
rm client.csr
```
client.key: Client private key

client.crt: Client certificate (signed by CA)


### Step 1: Build the Docker Image
This command creates a Docker image named my-nginx-parquet that includes NGINX with the configured certificate and the Parquet file.

Build the Docker image with the following command:

```bash
docker build -t my-nginx-parquet .
```

### Step 2: Run the NGINX Container
Start the container and map port 443 on your host to port 443 in the container:

```bash
docker run -d -p 443:443 --name nginx-parquet my-nginx-parquet
```

`-d`: Runs the container in detached mode.

`-p 443:443`: Maps port 443 on the host to port 443 in the container.

`--name nginx-parquet`: Names the container.


After running this command, the Parquet file will be accessible at https://localhost/data.parquet.

### Step 3: Install the DuckDB CLI
If the DuckDB CLI is not already installed:

Linux/macOS: Download the binary, unzip, and make it executable:
Replace vX.X.X with the latest version number.

```bash
wget https://github.com/duckdb/duckdb/releases/download/vX.X.X/duckdb_cli-linux-amd64.zip
unzip duckdb_cli-linux-amd64.zip
chmod +x duckdb
```

### Step 4: Test Latency without Certificate Verification

Start the DuckDB CLI:

```bash
duckdb
```

Set the DuckDB settings.

```bash
SET threads TO '12';
SET memory_limit = '4GB';
SET enable_object_cache = true;
SET external_threads TO 1;
```

```sql
.timer on
INSTALL httpfs;
LOAD httpfs;
SET enable_server_cert_verification = false;
SELECT * FROM read_parquet('https://localhost/data.parquet');
```

Observe the execution time displayed.

### Step 5: Test Latency with Certificate Verification Enabled

Start the DuckDB CLI:

```bash
duckdb
```

Set the DuckDB settings.

```bash
SET threads TO '12';
SET memory_limit = '4GB';
SET enable_object_cache = true;
SET external_threads TO 1;
```

Run the following commands in the DuckDB CLI:
Verify CA Certificate Path.

```sql
.timer on
INSTALL httpfs;
LOAD httpfs;
SET ca_cert_file = './certs/ca.crt';
SET enable_server_cert_verification = true;
SELECT * FROM read_parquet('https://localhost/data.parquet');
```

Observe the execution time displayed.

### Step 6: Testing with curl
This will fail - no client certificate
```bash
curl -v -k https://localhost/
``` 

This will succeed - with client certificate
```bash
curl -v -k --cert certs/client.crt --key certs/client.key https://localhost/data.parquet
```