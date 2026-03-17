# README_DATA

Esta carpeta contiene los datos utilizados por la aplicación de Streamlit.  
Todos los archivos ya vienen precargados y listos para usar; este README describe su contenido y propósito para que cualquier usuario pueda entenderlos fácilmente.

## Resumen de archivos

| Archivo | Formato | Descripción breve |
|---------|---------|-----------------|
| acces_log.xlsx | Excel | Control de acceso de los usuarios |
| lineups_register.xlsx | Excel | Alineaciones añadidas con equipos, posiciones, competiciones, coordenadas, sistema de juego y usuario que las insertó |
| list_players_register.xlsx | Excel | Jugadores añadidos a listas con equipo, posición, competición, usuario, nombre de la lista y observaciones (fichaje, observar, proyección) |
| message_from_users.xlsx | Excel | Mensajes enviados al administrador que sugieren la importación de nuevas competiciones desde Fbref |
| users.xlsx | Excel | Usuarios creados en la aplicación |
| players_stats.db | SQLite | Base de datos con los datos importados y tratados desde Fbref sobre jugadores de competiciones determinadas |

---

## Descripción detallada de los archivos

## Descripción detallada de los archivos (mejorada)

1. **acces_log.xlsx**  
   - **Descripción:** Registro completo de los accesos de los usuarios a la aplicación. Incluye fecha, hora, usuario y tipo de acción realizada, útil para control de actividad y auditoría.  
   - **Formato:** Excel  

2. **lineups_register.xlsx**  
   - **Descripción:** Alineaciones registradas en el sistema. Contiene equipos, posiciones, competiciones, coordenadas de los jugadores en el sistema, el sistema de juego seleccionado y el usuario que insertó la alineación. Sirve para análisis táctico y seguimiento histórico de alineaciones.  
   - **Formato:** Excel  

3. **list_players_register.xlsx**  
   - **Descripción:** Listas de jugadores añadidos por los usuarios. Incluye equipo, posición, competición, nombre de la lista, usuario que lo añadió y observaciones sobre su estado (fichaje, seguimiento, proyección). Permite organizar y filtrar jugadores según interés o evaluación.  
   - **Formato:** Excel  

4. **message_from_users.xlsx**  
   - **Descripción:** Mensajes enviados al administrador que sugieren la incorporación de nuevas competiciones desde Fbref. Contiene remitente, fecha y texto del mensaje, facilitando la gestión de solicitudes de datos adicionales.  
   - **Formato:** Excel  

5. **users.xlsx**  
   - **Descripción:** Información de los usuarios registrados en la aplicación. Incluye nombre, correo, rol y estado, esencial para control de acceso y permisos dentro del sistema.  
   - **Formato:** Excel  

6. **players_stats.db**  
   - **Descripción:** Base de datos SQLite con estadísticas de jugadores importadas y procesadas desde Fbref para competiciones determinadas. Contiene datos de rendimiento por jugador, equipo y competición, sirviendo como fuente principal para análisis y visualización dentro de la aplicación.  
   - **Formato:** SQLite Database (.db)  
   - **Notas:** Es el archivo central para consultas y generación de métricas en la app.