# ADR-001 — Ionic React para la base híbrida

## Estado

Aceptada para la base candidata `0.4.0-rc.1`.

## Contexto

La Sumativa 4 requiere un framework híbrido iOS/Android, un prototipo pequeño e
integración progresiva con el trabajo web. La base debe permitir que sus módulos
evolucionen sin duplicar contratos. El MVP Django y el mockup web existentes
deben conservarse.

## Alternativas consideradas

1. Mantener únicamente Django responsivo.
2. Construir una nueva aplicación con Flutter.
3. Incorporar Ionic con React y TypeScript.

## Criterios

- cumplimiento explícito del requisito híbrido;
- reutilización de experiencia, conceptos y recursos web;
- costo de reconstrucción en el plazo disponible;
- componentes adecuados para una interfaz móvil;
- separación clara del backend existente;
- compilación y despliegue web estático;
- trabajo paralelo por módulos;
- camino futuro hacia empaquetado móvil.

## Decisión

Usar Ionic React con TypeScript. La base se ejecuta primero como aplicación web
estática, usa componentes Ionic y navegación Ionic/React, y mantiene el dominio y
la persistencia separados de las páginas. Capacitor podrá evaluarse después para
empaquetado móvil, pero no se incorpora en esta tarea.

Esta elección no implica que Flutter o Django sean técnicamente incorrectos.
Django responsivo sigue siendo apropiado para el MVP web y Flutter podría ser una
buena alternativa con más tiempo y experiencia específica. Ionic reduce la
reconstrucción en el plazo de dos días y satisface directamente el requisito
híbrido.

## Consecuencias positivas

- Una sola base de código puede ejecutarse en navegador y evolucionar a móvil.
- Se reutilizan React, TypeScript, HTML y CSS.
- Ionic aporta componentes y patrones de navegación orientados a dispositivos.
- La salida `dist/` puede desplegarse como sitio estático.
- La separación por `features/` facilita dividir captura e histórico.
- La interfaz `NovedadRepository` permite sustituir `localStorage` por una API.

## Riesgos

- El paquete inicial de Ionic es mayor que un sitio HTML sencillo.
- `localStorage` no es una base de datos móvil ni una cola de sincronización.
- La sesión demostrativa no proporciona seguridad real.
- Un empaquetado futuro con Capacitor requiere configuración y pruebas nativas.
- Los módulos funcionales pueden divergir si cambian archivos comunes sin revisión.

## Medidas de mitigación

- Mantener el alcance pequeño y probar lint, repositorio, páginas base y build.
- Rotular como demostrativas las funciones locales.
- No guardar contraseñas ni incorporar datos reales.
- Congelar el contrato común durante el trabajo paralelo.
- Exigir revisión de cambios compartidos y pruebas después de cada integración.
- Documentar Amplify como preparación, sin inventar un despliegue.
