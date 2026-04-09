# 🧠 Claudio Bot - Capacidades y Características

Claudio no es solo un bot de Telegram; es un **Orquestador de Automatización basado en IA** diseñado específicamente para maximizar tu productividad con **n8n**.

---

## 🚀 Capacidades Principales

### 1. Creación de Workflows mediante Lenguaje Natural
Olvida arrastrar nodos manualmente para ideas simples. Solo dile a Claudio qué necesitas:
*   *"Crea un flujo que reciba un Webhook, guarde los datos en Google Sheets y me envíe un mensaje a Telegram"*
*   *"Haz un workflow para procesar correos de Gmail con OpenAI y guardarlos en Airtable"*

### 2. Acceso a +10,800 Plantillas (Templates)
Claudio tiene acceso a una biblioteca masiva para que no tengas que reinventar la rueda:
*   **2,700+ Plantillas Oficiales**: El catálogo completo de la biblioteca de n8n.
*   **8,100+ Plantillas de la Comunidad**: Flujos reales creados por expertos de todo el mundo, indexados localmente para búsquedas instantáneas.

### 3. Gestión Total de tu Instancia n8n
Controla tu servidor n8n desde el móvil:
*   **Listar**: Ver todos tus flujos y su estado actual (Activo/Inactivo).
*   **Activar/Desactivar**: Controla tus automatizaciones en producción sobre la marcha.
*   **Eliminar**: Limpia flujos individuales o toda tu instancia con comandos simples.
*   **Detalle**: Obtén la definición JSON de cualquier flujo para inspeccionarlo.

---

## 🧠 Inteligencia y Modelos Soporte

Claudio utiliza un sistema de **Proveedor Múltiple Dinámico** que garantiza que nunca te quedes sin servicio:

*   **Modelos Soportados**:
    *   **Anthropic**: Claude 3.5 Sonnet (Recomendado para lógica de nodos).
    *   **OpenAI**: GPT-4o y GPT-4 Turbo.
    *   **DeepSeek & GLM**: Alternativas de alta eficiencia y bajo costo.
    *   **Ollama**: Soporte para modelos locales (Llama 3, Mistral) para máxima privacidad.
*   **Auto-Fallback**: Si un proveedor (ej. Claude) falla o alcanza su límite de cuota, Claudio cambia automáticamente al siguiente (ej. GPT) sin interrumpir tu experiencia.

---

## 🛠️ Conocimiento Técnico Integrado

Claudio es un experto en las "tripas" de n8n:
*   **Sintaxis de Expresiones**: Conoce perfectamente cómo usar `{{ $json }}`, `{{ $node["Name"] }}`, `{{ $now }}` y funciones de JavaScript.
*   **Mejores Prácticas**: Te advertirá sobre errores comunes (ej. el uso de `$json.body` en webhooks).
*   **Base de Datos de Nodos**: Entiende los parámetros y operaciones de más de **1,300 nodos** únicos.

---

## 🔒 Seguridad de Nivel Producción

*   **Control de Acceso**: Solo los usuarios cuyos IDs de Telegram estén en la lista blanca (`ALLOWED_USERS`) pueden interactuar con Claudio.
*   **Comandos de Administrador**: Las funciones críticas de gestión de modelos y borrado masivo están restringidas a administradores.
*   **Ejecución Segura**: Implementado localmente o en VPS mediante servicios dedicados o contenedores Docker.
