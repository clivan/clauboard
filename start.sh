#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

info() { echo -e "${CYAN}[clauboard]${RESET} $1"; }
ok()   { echo -e "${GREEN}[ok]${RESET} $1"; }
warn() { echo -e "${YELLOW}[warn]${RESET} $1"; }
fail() { echo -e "${RED}[error]${RESET} $1"; exit 1; }

# ── 1. Verificar que la red exista (la crea el compose principal) ──────────
info "Verificando red clauboard-net..."

if ! docker network inspect clauboard-net &>/dev/null; then
    info "Red no existe, levantando stack principal para crearla..."
    docker compose -f "$SCRIPT_DIR/compose.yml" up -d --wait 2>/dev/null || true
fi

ok "Red clauboard-net disponible"

# ── 2. Infraestructura ─────────────────────────────────────────────────────
if [ ! -f "$SCRIPT_DIR/infra/.env" ]; then
    fail "Falta infra/.env — cópialo de infra/.env.example y completa las contraseñas"
fi

info "Levantando infraestructura (bases de datos y servicios compartidos)..."
docker compose -f "$SCRIPT_DIR/infra/compose.yml" \
    --env-file "$SCRIPT_DIR/infra/.env" \
    up -d

ok "Infraestructura lista"

# ── 3. Stack principal (proxy + backend + frontend) ────────────────────────
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    warn ".env de la raíz no existe — usando CLAUBOARD_PROJECTS_DIR por default (./clauboard-projects)"
fi

info "Levantando stack principal (proxy / backend / frontend)..."
docker compose -f "$SCRIPT_DIR/compose.yml" \
    up -d

ok "Stack principal listo"

# ── 4. Recarga nginx por si hay confs nuevos desde el último arranque ──────
info "Recargando nginx..."
docker exec clauboard-proxy nginx -s reload 2>/dev/null && ok "nginx recargado" || true

# ── 5. Verificar que el backend arrancó sin errores de import ─────────────
info "Verificando arranque del backend..."
sleep 2

if docker logs clauboard-backend --tail 30 2>&1 | grep -qE "ImportError|ModuleNotFoundError|Traceback"; then
    warn "El backend parece tener un error de arranque. Revisa:"
    warn "  docker logs clauboard-backend --tail 30"
else
    ok "Backend arrancó sin errores de import"
fi

# ── 6. Aviso si faltan imágenes propias por construir ──────────────────────
MISSING_IMAGES=()

for img in \
    clauboard/ros2-base:humble \
    clauboard/opencv:latest \
    clauboard/avr-baremetal:latest \
    clauboard/stm32-baremetal:latest \
    clauboard/esp32-baremetal:latest \
    clauboard/rpi-pico-baremetal-arm:latest
do
    if ! docker image inspect "$img" &>/dev/null; then
        MISSING_IMAGES+=("$img")
    fi
done

if [ ${#MISSING_IMAGES[@]} -gt 0 ]; then
    warn "Faltan imágenes propias por construir:"
    for img in "${MISSING_IMAGES[@]}"; do
        echo "    - $img"
    done
    warn "Corre los scripts de build en backend/app/registry/templates/ si vas a usar esos templates"
fi

# ── 7. Resumen ─────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${CYAN}  Clauboard listo${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "  Dashboard  →  ${GREEN}http://clauboard.localhost${RESET}"
echo -e "  API docs   →  ${GREEN}http://localhost:8000/docs${RESET}"
echo ""
docker ps --filter "name=clauboard" --format "  {{.Names}}\t{{.Status}}" 2>/dev/null
echo ""