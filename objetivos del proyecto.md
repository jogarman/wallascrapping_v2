# Objetivos de wallascrap v2

## 

### Segunda versión de Scrappeando_Wallapop. Esta versión tratará de estar compleamente integrada con los servicios de AWS. Especialmente con Lamdas

## Objetivo:
Scrappear regularmente y coste asumible ciertos articulos clave de wallapop, con especial incapie en los más comodities, entiendiedo por comodities aquellos en los que el valor es muy definido. Pongamos por ejemplo de comodity los iphone. El valor de un iphone dependerá del modelo, tipo, memoria y estado de la batería. Pero también de otros factores como la época del año, tiempo desde que apareció ese modelo, número de modelos desde que apareció ese modelo.... Sabemos que Apple es lo un ejemplo opuesto de comodity, pero el mercado de segunda mano si que puede entenderse así, siempre que conserve sus piezas originales, y no este apreciablemente rallado o golpeado. 
La idea es hacer arbitraje de precios y sacarme algún dinero comprando chollos rapidamente cuando aparecen y vendiendo en la época más demandada del año.

## El problema:
La primera versión de scrappeando Wallapop fracasó por haber sido desarrollada en python desde un PC windows y tratar de llevar el mismo código a la nube. Intenté implementarlo en un conetedor docker y llevarlo a ECS (sin exp. en docker, windows y con las librerías que usé resultó muy complejo) y luego creando una instancia de tamaño medium con un windows server 2025. Esta ultima solución funcionaba a medias:
* Era cara.
* La automatización de levantar y cerrar la instancia no s ehacía fácil,
* Fallaba ocasionalmente y debía también gestionar esta casuistica con más código
* Conectarme con SSH se hacía tedioso.

El proyecto hubiera termiando funcionando pero no me sobraba el tiempo. Si hubiera querido este proyecto en una instancia de EC2 debería haberlo desarrollado en un principio en Linux, no windows.

## La solución:
La forma más sencilla de implementar este proyecto usando Lambdas, el servicio de funciones serverless de AWS desde el principio.
Aprovecharé el código del otro proyecto en la medida de lo posible.

## Estructura del proyecto:
* Una seríe de Lamdas que se llamen entre sí en AWS. Ejecutar el código periodicamente y almacenar los datos en S3
* Emplear Power Bi o un programa de analitica en AWS para la visualización de estos datos. 
* Hacer un pequeño front en React.
** Elegir el elemento/s a buscar
** Elegir la periodicidad a buscar
** modificar whitelists y blacklists
