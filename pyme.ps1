#!/usr/bin/env pwsh

param(
    [string]$Action = "start"
)

function Write-Step {
    param([string]$Message)
    Write-Host "$Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "$Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "$Message" -ForegroundColor Red
}

function Show-Help {
    Write-Host "PYME Market - Script de Gestión" -ForegroundColor Green
    Write-Host ""
    Write-Host "Uso: .\pyme.ps1 [accion]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Acciones disponibles:" -ForegroundColor White
    Write-Host "  start    - Inicia todos los servicios (por defecto)"
    Write-Host "  stop     - Detiene todos los servicios"
    Write-Host "  restart  - Reinicia todos los servicios"
    Write-Host "  clean    - Detiene y limpia contenedores"
    Write-Host "  logs     - Muestra logs de todos los servicios"
    Write-Host "  status   - Muestra el estado de los contenedores"
    Write-Host "  help     - Muestra esta ayuda"
    Write-Host ""
}

switch ($Action.ToLower()) {
    "start" {
        Write-Host "Iniciando PYME Market..." -ForegroundColor Green
        Write-Step "Limpiando contenedores anteriores..."
        docker-compose down
        
        Write-Step "Levantando base de datos..."
        docker-compose up database --build -d
        
        Write-Step "Esperando a que la base de datos este lista..."
        Start-Sleep -Seconds 15
        
        Write-Step "Levantando todos los servicios..."
        docker-compose up auth products chat orders frontend --build -d
        
        Write-Success "¡PYME Market iniciado correctamente!"
        Write-Host ""
        Write-Host "URLs disponibles:" -ForegroundColor Yellow
        Write-Host "   Frontend:  http://localhost:5173" -ForegroundColor White
        Write-Host "   Auth:      http://localhost:8000" -ForegroundColor White
        Write-Host "   Products:  http://localhost:8001" -ForegroundColor White
        Write-Host "   Orders:    http://localhost:8002" -ForegroundColor White
        Write-Host "   Chat:      http://localhost:8003" -ForegroundColor White
        Write-Host "   Database:  localhost:5432" -ForegroundColor White
    }
    
    "stop" {
        Write-Host "Deteniendo PYME Market..." -ForegroundColor Red
        docker-compose down
        Write-Success "Servicios detenidos"
    }
    
    "restart" {
        Write-Host "Reiniciando PYME Market..." -ForegroundColor Yellow
        docker-compose down
        Start-Sleep -Seconds 3
        
        Write-Step "Levantando base de datos..."
        docker-compose up database --build -d
        Start-Sleep -Seconds 15
        
        Write-Step "Levantando todos los servicios..."
        docker-compose up auth products chat orders frontend --build -d
        
        Write-Success "¡PYME Market reiniciado correctamente!"
    }
    
    "clean" {
        Write-Host "Limpiando PYME Market..." -ForegroundColor Magenta
        docker-compose down -v
        docker system prune -f
        Write-Success "Limpieza completada"
    }
    
    "logs" {
        Write-Host "Mostrando logs..." -ForegroundColor Blue
        docker-compose logs --follow
    }
    
    "status" {
        Write-Host "Estado de los servicios:" -ForegroundColor Blue
        docker-compose ps
    }
    
    "help" {
        Show-Help
    }
    
    default {
        Write-Error "Acción no reconocida: $Action"
        Show-Help
    }
}
