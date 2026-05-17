% reglas.pl
% Motor de reglas de GameNest

% Una recomendación es válida si cumple las reglas principales:
% - edad suficiente según PEGI
% - plataforma compatible
% - precio dentro del presupuesto
% - tipo de juego compatible

recomendacion_valida(EdadUsuario, PlataformaUsuario, PresupuestoUsuario, TipoUsuario,
                     PegiJuego, PlataformaJuego, PrecioJuego, TipoJuego) :-
    edad_valida(EdadUsuario, PegiJuego),
    plataforma_valida(PlataformaUsuario, PlataformaJuego),
    presupuesto_valido(PresupuestoUsuario, PrecioJuego),
    tipo_valido(TipoUsuario, TipoJuego).


% El usuario puede jugar si su edad es igual o superior al PEGI del juego.
edad_valida(EdadUsuario, PegiJuego) :-
    EdadUsuario >= PegiJuego.


% La plataforma del juego debe coincidir con la plataforma preferida del usuario.
plataforma_valida(PlataformaUsuario, PlataformaJuego) :-
    PlataformaUsuario == PlataformaJuego.


% El precio del juego debe ser menor o igual que el presupuesto máximo del usuario.
presupuesto_valido(PresupuestoUsuario, PrecioJuego) :-
    PrecioJuego =< PresupuestoUsuario.


% El tipo de juego se considera válido si coincide con la preferencia del usuario.
tipo_valido(TipoUsuario, TipoJuego) :-
    TipoUsuario == TipoJuego.