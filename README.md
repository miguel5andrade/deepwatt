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

`$ sudo systemctl enable mtb-data-visualizer.service`

`$ sudo systemctl restart mtb-data-visualizer.service`

`$ sudo systemctl status mtb-data-visualizer.service`



## Backend API

### Instalar requirements da api

`$ pip install -r api_requirements.txt`

### correr api:

`$ python3 app.py`

### A api está a correr numa sessão tmux (tipo screen)

Para ver as sessões que existem:

`$ tmux ls` -> vai aparecer: mtb-data-visualizer-api: 1 windows (created Wed Dec 18 17:04:38 2024)

Para entrar na sessão:

`$ tmux a -t mtb-data-visualizer-api`

Para sair da sessão: ctrl+b (soltar) d

# Service

### conteudos do mtb-data-visualizer.service:

[Unit]
Description=Vue.js Application

[Service]
ExecStart=/usr/local/bin/serve -s /home/mtb/mtb-data-view/mtb-data-visualizer/dist -l tcp://0.0.0.0:8888
Restart=always
User=mtb
Group=mtb
Environment=PATH=/usr/bin:/usr/local/bin
Environment=NODE_ENV=production
WorkingDirectory=/home/mtb/mtb-data-view/mtb-data-visualizer/

[Install]
WantedBy=multi-user.target
