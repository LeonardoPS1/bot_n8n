#!/bin/bash
# Script para subir el repositorio bot_n8n a GitHub

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Subir bot_n8n a GitHub ===${NC}"
echo ""

# Paso 1: Crear repositorio en GitHub (manual)
echo -e "${YELLOW}Paso 1: Crear repositorio en GitHub${NC}"
echo "1. Ve a https://github.com/new"
echo "2. Crea un nuevo repositorio llamado 'bot_n8n'"
echo "3. NO agregues README, .gitignore o license (ya existen)"
echo "4. Copia la URL del repositorio (ej: https://github.com/leonardospedaletti/bot_n8n.git)"
echo ""

read -p "Pega la URL del repositorio de GitHub: " GITHUB_URL

# Paso 2: Agregar remote
echo -e "${YELLOW}Paso 2: Configurar remote${NC}"
git remote add origin $GITHUB_URL
git remote -v

# Paso 3: Renombrar branch a main (opcional, moderno)
echo -e "${YELLOW}Paso 3: Renombrar branch a main${NC}"
git branch -M main

# Paso 4: Push a GitHub
echo -e "${YELLOW}Paso 4: Subir código a GitHub${NC}"
git push -u origin main

echo ""
echo -e "${GREEN}✅ Repositorio subido exitosamente!${NC}"
echo ""
echo "Visita tu repositorio en: $GITHUB_URL"
