# Publicar gratis con la API de YouTube: configuración única (30–45 min)

Con esto, GitHub Actions sube los videos con la API oficial de YouTube. No usa Zapier ni créditos. La API permite **100 subidas por día** y los videos salen **públicos** (Google ya no bloquea en privado las subidas de proyectos sin verificar).

> 🔒 Los secretos (ID, secreto y tokens) van **solo** en GitHub → Secrets. Nunca los pegues en el chat ni en un archivo del repo: el repo es público.

## 1. Crear el canal nuevo (curiosidades)
1. Entra a YouTube con tu cuenta → foto de perfil → **Configuración** → **Agregar o administrar canales** → **Crear un canal**. Ponle el nombre que elijas.
2. Verifica el canal por teléfono en <https://www.youtube.com/verify>. Sin esto no se pueden poner miniaturas propias.
3. Copia el **ID del canal** (empieza con `UC…`) desde <https://www.youtube.com/account_advanced> estando en ese canal. Me lo vas a pasar a mí; ese dato no es secreto.

## 2. Proyecto de Google Cloud (una sola vez)
1. Entra a <https://console.cloud.google.com> → arriba, **Seleccionar proyecto** → **Proyecto nuevo** → nombre `videos-canales` → **Crear**.
2. Menú → **APIs y servicios** → **Biblioteca** → busca **YouTube Data API v3** → **Habilitar**.
3. Menú → **APIs y servicios** → **Pantalla de consentimiento de OAuth** (o **Google Auth Platform**) → **Comenzar**:
   - Nombre de la app: `videos-canales`. Correo: el tuyo.
   - Público: **Externo**. Contacto: tu correo. Acepta y **Crear**.
   - En **Público** (Audience), toca **Publicar app** → **Confirmar**, para que quede **En producción**. ⚠️ Si queda "En prueba", los tokens vencen a los 7 días.
4. **Clientes** (o **Credenciales**) → **Crear cliente** (ID de cliente de OAuth):
   - Tipo: **Aplicación web**.
   - **URI de redireccionamiento autorizados** → agrega `https://developers.google.com/oauthplayground`
   - **Crear** → copia el **ID de cliente** y el **Secreto del cliente** (guárdalos en un lugar seguro).

## 3. Un token por canal (repetir 3 veces: Pulso IA, Peque Planeta y el nuevo)
1. Abre <https://developers.google.com/oauthplayground>.
2. Engranaje ⚙️ (arriba a la derecha) → marca **Use your own OAuth credentials** → pega el ID y el secreto.
3. A la izquierda, en **Input your own scopes**, pega esto (es una sola línea, con un espacio en el medio):
   `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly`
   → **Authorize APIs**.
4. Elige tu cuenta y, cuando pregunte, **el canal correcto** (por ejemplo, Pulso IA).
   Si aparece "Google no verificó esta app": **Configuración avanzada** → **Ir a videos-canales** → **Continuar / Permitir**. Es tu propia app, así que es normal.
5. Toca **Exchange authorization code for tokens** → copia el **Refresh token** (empieza con `1//`).
6. Para el siguiente canal, vuelve a **Step 1** y repite desde el punto 3, eligiendo el otro canal.

## 4. Guardar todo en GitHub
Repo `videos-canales` → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**. Crea estos cinco:

| Nombre | Valor |
|---|---|
| `YT_CLIENT_ID` | ID de cliente del paso 2 |
| `YT_CLIENT_SECRET` | Secreto del cliente del paso 2 |
| `YT_REFRESH_PULSO` | Refresh token de Pulso IA |
| `YT_REFRESH_PEQUE` | Refresh token de Peque Planeta |
| `YT_REFRESH_CURIOSIDADES` | Refresh token del canal nuevo |

## 5. Avísame
Pásame el **nombre** y el **ID `UC…`** del canal nuevo. Con eso:
- Hago una subida de prueba.
- Armo la tarea diaria del canal de curiosidades.
- Paso Pulso IA y Peque Planeta a la API (sin tope de Zapier). Zapier queda de respaldo.

Antes de subir, el sistema revisa que cada token sea del canal correcto. Si no coincide, no sube nada y deja el error en `publicados/`.
