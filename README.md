# DeepWatt Website

## Frontend

### Instalar dependencias:

`$ npm install`

### Correr para testes:

`$ npm run dev`

### Dar deploy:

`$ npm run build`
(cria pasta chamada dist com os ficheiros compilados)

`$ sudo systemctl daemon-reload`

`$ sudo systemctl enable deepwaat-frontend.service`

`$ sudo systemctl restart deepwaat-frontend.service`

`$ sudo systemctl status deepwaat-frontend.service`



## Backend API

### Instalar requirements da api

`$ pip install -r requirements.txt`

### correr api:

`$ python3 app.py`

### A api está a correr numa sessão tmux (tipo screen)

Para ver as sessões que existem:

`$ tmux ls` -> vai aparecer: deepwaat-frontend-api: 1 windows (created Wed Dec 18 17:04:38 2024)

Para entrar na sessão:

`$ tmux a -t deepwaat-frontend-api`

Para sair da sessão: ctrl+b (soltar) d

### Budget Publisher

* Runs every 30 seconds, publishes messages with the current budget usage to the feedback nodes




# Service

### conteudos do mtb-data-visualizer.service:

```
[Unit]
Description=Vue.js Application

[Service]
ExecStart=/usr/local/bin/serve -s /home/user/deepwaat-frontend/dist -l tcp://0.0.0.0:8888
Restart=always
User=mtb
Group=mtb
Environment=PATH=/usr/bin:/usr/local/bin
Environment=NODE_ENV=production
WorkingDirectory=/home/user/deepwaat-frontend/

[Install]
WantedBy=multi-user.target
```

* to use serve command: 

`sudo npm install -g serve` 