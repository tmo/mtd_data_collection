# sudo docker build -t myhttpd .

FROM httpd:2.4
COPY ./server_files/html/* /usr/local/apache2/htdocs/
# COPY ./my-httpd.conf /usr/local/apache2/conf/httpd.conf

RUN apt update
RUN apt install iputils-ping -y
RUN apt install net-tools -y