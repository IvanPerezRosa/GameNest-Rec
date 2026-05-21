# GameNest-Rec

GameNest-Rec es una aplicación web de recomendación personalizada de videojuegos.  
El sistema permite a los usuarios registrarse, iniciar sesión, configurar sus preferencias y recibir recomendaciones adaptadas a su perfil.

Las recomendaciones se generan teniendo en cuenta géneros favoritos, plataformas disponibles, tipo de juego, edad, presupuesto máximo y reglas lógicas implementadas con Prolog.

---

## Funcionalidades principales

- Registro de usuarios.
- Inicio y cierre de sesión.
- Perfil persistente de usuario.
- Edición de preferencias.
- Selección de múltiples plataformas.
- Selección de múltiples géneros favoritos.
- Selección de Singleplayer, Multiplayer o ambos.
- Recomendaciones personalizadas de videojuegos.
- Desglose de puntuación interna para explicar cada recomendación.
- Validación lógica de recomendaciones mediante Prolog.
- Catálogo de juegos almacenado en CSV.
- Importador opcional de juegos desde Steam/SteamSpy.

---

## Tecnologías utilizadas

- Python
- Flask
- Pandas
- Prolog
- PySwip
- HTML
- CSS
- CSV
- Git / GitHub

---

## Estructura del proyecto

```text
GameNest-Rec/
│
├── data/
│   ├── juegos.csv
│   ├── usuarios.csv
│   └── valoraciones.csv
│
├── prolog/
│   └── reglas.pl
│
├── src/
│   ├── cargar_datos.py
│   ├── gestionar_usuarios.py
│   ├── importar_steam.py
│   ├── motor_prolog.py
│   └── recomendador_contenido.py
│
├── web/
│   ├── app.py
│   ├── templates/
│   └── static/
│
├── requirements.txt
├── README.md
└── .gitignore