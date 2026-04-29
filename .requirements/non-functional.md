# Requerimientos No Funcionales

Atributos de **calidad** y restricciones del sistema de gestión documental. Complementan los [requerimientos funcionales](requerimiento_funcional.md): los RF dicen *qué* hace el sistema; los RNF dicen *qué tan bien* o bajo qué condiciones.

**Referencias:** [Autenticación](auth.md) · [Contexto operacional](../docs/contexto_operacional.md) · [Problema](../docs/problema.md)

---

## RNF1 — Seguridad

| ID | Requisito | Criterio orientador |
| --- | --- | --- |
| RNF1.1 | **Autenticación** mediante Supabase Auth (o equivalente acordado con el proyecto). | Sesiones gestionadas por el proveedor; no almacenar contraseñas en texto plano en lógica propia. |
| RNF1.2 | **Autorización** basada en roles, alineada con RF5.1. | Operaciones denegadas sin permiso; sin filtrado de datos entre roles no autorizados. |
| RNF1.3 | **Datos en tránsito** sobre HTTPS en entornos desplegados. | Certificados válidos en producción. |
| RNF1.4 | **Principio de mínimo privilegio** en base de datos y almacenamiento (p. ej. políticas RLS en Supabase cuando aplique). | Acceso a filas y objetos acotado al usuario o rol. |

Comportamiento de login, logout y rutas protegidas: [auth.md](auth.md).

---

## RNF2 — Rendimiento

| ID | Requisito | Criterio orientador |
| --- | --- | --- |
| RNF2.1 | **Consultas** (listados y búsqueda) con tiempos de respuesta percibidos como rápidos en condiciones de red institucionales típicas. | Indicadores de carga en operaciones largas; paginación o límites donde aplique. |
| RNF2.2 | **Carga de archivos** optimizada (tamaños máximos declarados, retroalimentación al usuario, posibilidad de reintento ante fallo transitorio). | Mensajes claros ante rechazo o error de red. |

Los valores numéricos exactos (SLA) pueden fijarse en una versión posterior según mediciones en el entorno real.

---

## RNF3 — Usabilidad

| ID | Requisito | Criterio orientador |
| --- | --- | --- |
| RNF3.1 | **Interfaz intuitiva** para tareas frecuentes: iniciar sesión, subir documento, buscar, abrir o descargar. | Flujos principales alcanzables con pocas acciones desde el panel. |
| RNF3.2 | **Navegación sencilla** entre módulos (documentos, búsqueda, administración según rol). | Estado actual del sistema reconocible (por ejemplo, usuario logueado, errores legibles). |

---

## RNF4 — Disponibilidad y acceso

| ID | Requisito | Criterio orientador |
| --- | --- | --- |
| RNF4.1 | **Acceso vía navegador web** moderno, sin instalación de cliente dedicado para usuarios finales. | Compatibilidad con los navegadores objetivo definidos por despliegue (documentar lista en README o manual). |

---

## RNF5 — Escalabilidad

| ID | Requisito | Criterio orientador |
| --- | --- | --- |
| RNF5.1 | Arquitectura que **admita crecimiento** de usuarios y volumen de documentos sin rediseño completo (capas separadas, almacenamiento gestionado). | Uso de servicios escalables (p. ej. Supabase, Vercel) según el stack acordado. |

---

## RNF6 — Mantenibilidad

| ID | Requisito | Criterio orientador |
| --- | --- | --- |
| RNF6.1 | **Código modular** y estructura de proyecto coherente con el stack (Next.js / React / Supabase). | Facilita cambios localizados y pruebas. |
| RNF6.2 | **Buenas prácticas** (tipado, convenciones del repositorio, revisión de dependencias). | Reduce deuda técnica y riesgo de regresiones. |

---

## RNF7 — Cumplimiento y datos personales (orientador)

| ID | Requisito | Criterio orientador |
| --- | --- | --- |
| RNF7.1 | En despliegue institucional, considerar la **normativa colombiana aplicable** a datos personales y habeas data, así como políticas internas de la IPS sobre retención y acceso a documentación administrativa. | Revisión jurídica / de protección de datos antes de producción; registro de tratamiento acordado con la institución. |

Este ítem no sustituye asesoría legal; documenta la expectativa de que el sistema opere en un marco regulado.

---

## Relación con autenticación

Los criterios de aceptación de [auth.md](auth.md) materializan parte de RNF1 y de los RF de gestión de usuarios (inicio y cierre de sesión, protección de rutas).
