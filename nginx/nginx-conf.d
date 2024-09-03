upstream app {
    server ORT:8000
}


server {
    listen 545;
    server_name 94.241.141.190;

    location /staticfiles/ {
        alias /var/www/ORT/static/;
    }

    location / {
        proxy_pass http://ort:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
