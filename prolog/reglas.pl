% reglas.pl
% Motor de reglas de GameNest

% Una recomendación es válida si cumple:
% - edad suficiente según PEGI
% - plataforma compatible
% - precio dentro del presupuesto
% - tipo de juego compatible

recomendacion_valida(EdadUsuario, PlataformasUsuario, PresupuestoUsuario, TiposUsuario,
                     PegiJuego, PlataformaJuego, PrecioJuego, TipoJuego) :-
    edad_valida(EdadUsuario, PegiJuego),
    plataforma_valida(PlataformasUsuario, PlataformaJuego),
    presupuesto_valido(PresupuestoUsuario, PrecioJuego),
    tipo_valido(TiposUsuario, TipoJuego).


% El usuario puede jugar si su edad es igual o superior al PEGI del juego.
edad_valida(EdadUsuario, PegiJuego) :-
    EdadUsuario >= PegiJuego.


% La plataforma del juego debe estar entre las plataformas del usuario.
plataforma_valida(PlataformasUsuario, PlataformaJuego) :-
    member(PlataformaJuego, PlataformasUsuario).


% El precio del juego debe ser menor o igual que el presupuesto máximo.
presupuesto_valido(PresupuestoUsuario, PrecioJuego) :-
    PrecioJuego =< PresupuestoUsuario.


% El tipo del juego debe estar entre los tipos preferidos del usuario.
tipo_valido(TiposUsuario, TipoJuego) :-
    member(TipoJuego, TiposUsuario).