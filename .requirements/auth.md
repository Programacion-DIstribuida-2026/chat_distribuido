# Autenticación y sesión

**Ámbito:** acceso al sistema de gestión documental (IPS Salud Integral) con correo y contraseña, usando **Supabase Auth**, y protección de rutas en la aplicación **Next.js**.

**Trazabilidad:** [requerimiento_funcional.md](requerimiento_funcional.md) **RF1.1** (altas de usuario), **RF1.2**, **RF1.3**, **RF1.4** (roles); [non-functional.md](non-functional.md) **RNF1.1**, **RNF1.2**.

**Política de seguridad (altas):** quien **no** tenga usuario creado en el sistema **no** puede registrarse por sí mismo. Para obtener acceso, la persona debe ser **dada de alta por un administrador**, quien es el **único** autorizado a **crear usuarios** y **definir o modificar sus roles**. Esto reduce superficie de ataque (sin cuentas anónimas) y alinea el acceso con la gobernanza de la IPS.

**Nota de idioma:** los criterios están en español para alinearlos con el resto de la documentación del proyecto.

---

## Historias de usuario

### Acceso

Como **usuario o administrador** con cuenta ya creada, quiero **iniciar y cerrar sesión de forma segura** para **usar solo las funciones permitidas por mi rol**.

### Gobierno de cuentas (solo administrador)

Como **administrador**, quiero **registrar a los usuarios y asignarles su rol** para **que solo personal autorizado acceda al sistema**, sin autoregistro público.

---

## Criterios de aceptación

### CA1: Inicio de sesión exitoso

**Dado** que un administrador me dio de alta y tengo credenciales activas  
**Cuando** ingreso un correo y una contraseña válidos en la página de inicio de sesión y envío el formulario  
**Entonces** soy redirigido al inicio (o panel) correspondiente a mi rol y mi sesión queda establecida

### CA2: Credenciales inválidas

**Dado** que estoy en la página de inicio de sesión  
**Cuando** ingreso un correo o una contraseña incorrectos  
**Entonces** veo un mensaje de error apropiado (por ejemplo, credenciales inválidas) **sin** revelar si el correo existe o no en el sistema

### CA3: Validación de correo

**Dado** que estoy en la página de inicio de sesión  
**Cuando** envío el formulario con un formato de correo inválido  
**Entonces** veo un error de validación **antes** o al enviar, según el diseño del formulario, y no se considera un intento de autenticación exitoso

### CA4: Contraseña en acceso

**Dado** que la política del producto exige reglas de contraseña en el formulario de acceso (longitud u otras)  
**Cuando** no las cumplo  
**Entonces** veo un mensaje claro antes de enviar o al validar, según el diseño

> La **primera contraseña** o el **enlace de activación** pueden venir del flujo de alta por administrador (invitación por correo, contraseña temporal, etc.); alinear con la implementación en Supabase.

### CA5: Cierre de sesión

**Dado** que tengo una sesión activa  
**Cuando** activo “Cerrar sesión”  
**Entonces** la sesión se invalida en el cliente y en el flujo de Supabase según corresponda, y soy redirigido a la página de inicio de sesión

### CA6: Rutas protegidas

**Dado** que **no** tengo sesión válida  
**Cuando** intento acceder a una ruta protegida de la aplicación  
**Entonces** soy redirigido a la página de inicio de sesión (u otra ruta pública definida)

### CA7: Sin autoregistro público

**Dado** que soy una persona **sin** cuenta en el sistema  
**Cuando** accedo a las pantallas públicas de la aplicación (p. ej. login)  
**Entonces** **no** puedo completar un flujo de “crear cuenta” o registro autónomo: el acceso depende de que un **administrador** me haya registrado previamente

### CA8: Alta de usuario y roles solo por administrador

**Dado** que estoy autenticado como **administrador**  
**Cuando** utilizo el flujo de alta de usuario (datos requeridos, correo, **rol inicial**)  
**Entonces** el nuevo usuario queda registrado en el sistema de autenticación y con el **rol definido por el administrador**; ningún otro rol puede realizar esta operación desde la UI (y las APIs deben negarla a no administradores)

### CA9: Usuario no administrador no registra ni asigna roles

**Dado** que estoy autenticado como **usuario administrativo** (no administrador)  
**Cuando** intento abrir el módulo de gestión de usuarios o invocar operaciones equivalentes (API / acciones de servidor)  
**Entonces** el sistema **deniega** el acceso (interfaz no disponible y/o respuesta **403** / error de autorización coherente)

---

## Casos de prueba (checklist)

- [ ] CP1: Credenciales válidas de usuario dado de alta por admin → redirección correcta según rol
- [ ] CP2: Contraseña incorrecta → mensaje de error, sin acceso
- [ ] CP3: Correo vacío → validación
- [ ] CP4: Formato de correo inválido → validación
- [ ] CP5: Reglas de contraseña en login (si aplican) → validación coherente
- [ ] CP6: Cierre de sesión → sesión cerrada y redirección a login
- [ ] CP7: Usuario no autenticado en ruta protegida → redirección a login
- [ ] CP8: Sin sesión → **no** existe registro público usable (ni enlaces que lo permitan sin admin)
- [ ] CP9: Administrador → alta de usuario con rol; el nuevo usuario puede iniciar sesión según ese rol
- [ ] CP10: Usuario administrativo → **no** puede alta de usuarios ni cambiar roles

---

## Fuera de alcance (versión actual)

- **Autoregistro** o registro abierto en Internet por cualquier visitante
- Inicio de sesión con proveedores sociales (Google, GitHub, etc.)
- Flujo completo de recuperación de contraseña (puede planificarse como mejora)
- Autenticación multifactor (MFA)

### Nota de despliegue / primer administrador

La creación del **primer** usuario administrador (bootstrap) puede hacerse por **script**, panel de Supabase o procedimiento acordado con la institución; debe quedar fuera del alcance del “autoregistro” de usuarios finales y documentarse en el manual de instalación.

---

## Referencias cruzadas

| Tema | Documento |
| --- | --- |
| Actores y flujo operativo | [contexto_operacional.md](../docs/contexto_operacional.md) |
| Lista RF de usuarios y seguridad | [requerimiento_funcional.md](requerimiento_funcional.md) |
| Calidad de seguridad y despliegue | [non-functional.md](non-functional.md) |
| Flujos detallados (login, logout, gestión de usuarios) | [use-cases.md](use-cases.md) (CU1, CU4, CU6) |
