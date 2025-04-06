# DeepWatt Website

## Frontend

### Instalar dependencias:

`$ npm install`

### Correr para testes:

`$ npm run dev`

### Dar deploy:

`$ npm run build`
(cria pasta chamada dist com os ficheiros compilados)




## Backend API

### Instalar requirements da api

`go mod tidy`

### Compilar:

`go build .`

### Correr:

`./backend-go`

### A api está a correr numa sessão tmux (tipo screen)

Para ver as sessões que existem:

`tmux ls` -> vai aparecer: deepwaat-frontend-api: 1 windows (created Wed Dec 18 17:04:38 2024)

Para entrar na sessão:

`tmux a -t deepwaat-frontend-api`

Para sair da sessão: ctrl+b (soltar) d

### Budget Publisher

* Runs every 30 seconds, publishes messages with the current budget usage to the feedback nodes



