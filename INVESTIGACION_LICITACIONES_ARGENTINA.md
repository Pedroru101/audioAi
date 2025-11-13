# Investigación de Mercado: Sistema de Licitaciones Argentina

## Fecha: 13 de Noviembre de 2025

---

## 📋 Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Análisis del Mercado](#análisis-del-mercado)
3. [Portales Oficiales](#portales-oficiales)
4. [Competidores](#competidores)
5. [Stack Tecnológico Recomendado](#stack-tecnológico-recomendado)
6. [Arquitectura del Sistema](#arquitectura-del-sistema)
7. [Plan de Desarrollo](#plan-de-desarrollo)
8. [Requisitos Mínimos (MVP)](#requisitos-mínimos-mvp)
9. [Fases de Implementación](#fases-de-implementación)
10. [Estimaciones y Recursos](#estimaciones-y-recursos)

---

## 🎯 Resumen Ejecutivo

### Oportunidad de Mercado

El mercado de licitaciones públicas en Argentina presenta una oportunidad significativa para empresas que buscan facilitar el acceso y análisis de oportunidades de negocio con el Estado. Actualmente existen:

- **Portales oficiales fragmentados** a nivel nacional, provincial y municipal
- **Competidores establecidos** con soluciones limitadas
- **Necesidad de automatización** y análisis inteligente con IA
- **Falta de integración** entre diferentes fuentes de datos

### Propuesta de Valor

Sistema integral que:
- ✅ Centraliza licitaciones de múltiples fuentes (nacional, provincial, municipal)
- ✅ Analiza automáticamente documentos con IA
- ✅ Proporciona insights sobre municipios y requisitos
- ✅ Ofrece chatbot inteligente para consultas
- ✅ Genera alertas personalizadas
- ✅ Interfaz moderna y fácil de usar

---

## 📊 Análisis del Mercado

### 1. Portales Oficiales Gubernamentales

#### A. Nivel Nacional

**COMPR.AR** (https://comprar.gob.ar/)
- Portal oficial de compras públicas del gobierno nacional
- Gestiona licitaciones de bienes y servicios
- Sistema electrónico para organismos nacionales
- **Estado:** Activo y en funcionamiento

**CONTRAT.AR** (https://contratar.gob.ar/)
- Plataforma para licitaciones de obra pública
- Gestión de concesiones y contratos de infraestructura
- Procesos publicados según estándar OCDS (Open Contracting Data Standard)
- **Estado:** Activo y en funcionamiento

**Oficina Nacional de Contrataciones (ONC)**
- Organismo rector del sistema de contrataciones
- Publica datos abiertos en formato estándar
- Implementa políticas de transparencia

#### B. Nivel Provincial y Municipal

**Portales identificados:**
- Buenos Aires: https://www.gba.gob.ar/infraestructura/licitaciones
- San Juan: https://licitaciones.sanjuan.gob.ar/
- Rosario: https://www.rosario.gob.ar/sitio/licitaciones
- Mendoza: https://www.mendoza.gov.ar/compras/

**Características:**
- Cada provincia/municipio tiene su propio sistema
- No existe estandarización entre portales
- Formatos y estructuras de datos diferentes
- Actualización variable según jurisdicción

### 2. Datos Abiertos

**Datos.gob.ar** (https://datos.gob.ar/)
- Portal nacional de datos abiertos
- Datasets de contrataciones disponibles
- Implementa estándar CKAN para API
- Formato: JSON, CSV, según estándar OCDS

**API CKAN disponible:**
```
GET https://datos.gob.ar/api/3/action/package_search?q=contrataciones
GET https://datos.gob.ar/api/3/action/package_show?id={dataset_id}
GET https://datos.gob.ar/api/3/action/datastore_search?resource_id={resource_id}
```

**Ventajas:**
- Acceso programático sin restricciones
- Datos estructurados
- Actualizaciones periódicas
- Estándar internacional (OCDS)

**Limitaciones:**
- No todos los organismos publican en tiempo real
- Algunas jurisdicciones no están integradas
- Calidad de datos variable

---

## 🏢 Competidores

### 1. LatamCompra
**Características:**
- Cobertura en 17 países de Latinoamérica
- Incluye Argentina, Brasil, Chile, Colombia, etc.
- Empresa establecida desde 2016
- Más de 250 empleados

**Servicios:**
- Alertas de licitaciones
- Reportes sobre proveedores y compradores
- Análisis de competencia
- Catálogos y precios

**Fortalezas:**
- Presencia regional consolidada
- Base de datos extensa
- Soporte multipaís

**Debilidades:**
- Interfaz desactualizada
- Falta de IA avanzada
- Análisis manual de documentos

### 2. ArgentinaLicitaciones.com
**Características:**
- Portal especializado en Argentina
- Recopilación de licitaciones públicas
- Sistema de alertas por email

**Servicios:**
- Búsqueda de licitaciones
- Notificaciones diarias
- Información sobre procesos

**Fortalezas:**
- Enfoque local
- Base de usuarios establecida

**Debilidades:**
- UI/UX anticuado
- Sin análisis con IA
- Funcionalidades limitadas

### 3. Plataformas Informativas
- **Diario de Licitaciones**: Portal de noticias
- **Infosisscon**: Portal de difusión
- Servicios básicos de información

### 4. Oportunidades vs Competidores

**Diferenciadores clave del nuevo sistema:**

| Característica | Competidores | Nuestro Sistema |
|---|---|---|
| **Interfaz moderna** | ❌ Desactualizada | ✅ React moderno, responsive |
| **Análisis con IA** | ❌ Manual o limitado | ✅ IA avanzada (GPT-4, OCR) |
| **Chatbot inteligente** | ❌ Sin chatbot | ✅ Asistente IA con RAG |
| **Análisis de municipios** | ❌ No disponible | ✅ Insights por jurisdicción |
| **Dockerizado** | ❌ No | ✅ Fácil deployment |
| **Multi-fuente** | ⚠️ Limitado | ✅ Nacional + Provincial + Municipal |
| **API abierta** | ❌ Cerrada/limitada | ✅ API REST completa |

---

## 💻 Stack Tecnológico Recomendado

### Frontend

**Framework Base:** React 18+ con Vite
- Build rápido y optimizado
- Hot Module Replacement (HMR)
- Bundle pequeño

**UI Framework:** Material UI (MUI) o Chakra UI
- Componentes modernos y accesibles
- Personalización flexible
- Documentación excelente
- Ecosystem maduro

**Alternativa:** Tailwind CSS + Headless UI
- Control total del diseño
- Utility-first approach
- Performance óptimo

**Estado Global:** Zustand o React Context + React Query
- React Query para data fetching
- Cache inteligente
- Manejo de estados asíncronos

**Routing:** React Router v6

**Visualización de Datos:**
- Recharts o Chart.js para gráficos
- React Table para tablas complejas

**Containerización:**
- Multi-stage Docker build
- Nginx para servir static files
- Optimizado para producción

### Backend

**Framework:** FastAPI (Python)
- Performance excelente
- Type hints nativos
- Documentación automática (OpenAPI/Swagger)
- Async/await nativo
- Validación con Pydantic

**Base de Datos:**
- **PostgreSQL** para datos relacionales
- **Redis** para cache y queues
- **Elasticsearch** para búsqueda full-text (opcional fase 2)

**Web Scraping:**
- **Scrapy** para crawling estructurado
- **BeautifulSoup4** para parsing
- **Selenium** o **Playwright** para sitios con JavaScript
- **Schedule** para tareas periódicas

**Procesamiento de Documentos:**
- **PyMuPDF (fitz)** para PDFs estructurados
- **OCRmyPDF + Tesseract** para PDFs escaneados
- **EasyOCR** como alternativa
- **pdfplumber** para tablas

**IA y Análisis:**
- **OpenAI API (GPT-4)** para análisis de texto
- **LangChain** para RAG y chains
- **ChromaDB** o **Pinecone** para vector database
- **Sentence Transformers** para embeddings

**Procesamiento Asíncrono:**
- **Celery** para tareas background
- **Redis** como message broker

**Containerización:**
- Docker multi-stage builds
- Docker Compose para desarrollo
- Health checks y restart policies

### Infrastructure

**Deployment:**
- Docker + Docker Compose
- Nginx como reverse proxy
- SSL/TLS con Let's Encrypt

**Monitoring (Fase 2):**
- Prometheus + Grafana
- Logs centralizados

**CI/CD (Fase 2):**
- GitHub Actions
- Tests automatizados

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  React + MUI/Chakra UI + Docker + Nginx                     │
│  - Dashboard principal                                       │
│  - Búsqueda y filtros                                       │
│  - Detalle de licitaciones                                  │
│  - Chatbot IA                                               │
│  - Análisis de municipios                                   │
└────────────────┬────────────────────────────────────────────┘
                 │ REST API (HTTPS)
┌────────────────┴────────────────────────────────────────────┐
│                         BACKEND                              │
│  FastAPI + Python + Docker                                  │
├─────────────────────────────────────────────────────────────┤
│  API REST Layer                                             │
│  - Endpoints de licitaciones                                │
│  - Autenticación (JWT)                                      │
│  - Rate limiting                                            │
├─────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                       │
│  - Búsqueda y filtrado                                      │
│  - Análisis con IA                                          │
│  - Generación de insights                                   │
│  - Chatbot con RAG                                          │
├─────────────────────────────────────────────────────────────┤
│  Data Collection Layer                                      │
│  - Scrapers (Scrapy)                                        │
│  - API Integrations (CKAN)                                  │
│  - Document Processors (OCR)                                │
│  - Celery Tasks (async)                                     │
└────┬─────────┬──────────┬──────────┬────────────────────────┘
     │         │          │          │
┌────┴───┐ ┌──┴─────┐ ┌──┴─────┐ ┌─┴──────────┐
│ PostgreSQL │ │ Redis  │ │ Chroma │ │   OpenAI   │
│  (Main DB) │ │(Cache) │ │ (RAG)  │ │    API     │
└────────┘ └────────┘ └────────┘ └────────────┘
     │
     │
┌────┴────────────────────────────────────────────────────────┐
│              EXTERNAL SOURCES                                │
├─────────────────────────────────────────────────────────────┤
│  - datos.gob.ar (API CKAN)                                  │
│  - COMPR.AR (Web Scraping)                                  │
│  - CONTRAT.AR (Web Scraping)                                │
│  - Portales Provinciales (Web Scraping)                     │
│  - Portales Municipales (Web Scraping)                      │
└─────────────────────────────────────────────────────────────┘
```

### Componentes Principales

#### 1. Frontend (React + Docker)

**Páginas principales:**
- **Dashboard:** Vista general, estadísticas, licitaciones recientes
- **Búsqueda:** Filtros avanzados (categoría, monto, fecha, ubicación)
- **Detalle:** Información completa de licitación + análisis IA
- **Municipios:** Perfiles de municipios con histórico
- **Alertas:** Configuración de notificaciones
- **Chatbot:** Asistente IA integrado

**Features:**
- Responsive design
- Dark/light mode
- Lazy loading
- PWA capabilities (fase 2)

#### 2. Backend API (FastAPI)

**Endpoints principales:**
```python
# Licitaciones
GET    /api/v1/licitaciones          # Lista con paginación
GET    /api/v1/licitaciones/{id}     # Detalle
GET    /api/v1/licitaciones/search   # Búsqueda avanzada
POST   /api/v1/licitaciones/analyze  # Análisis IA

# Municipios
GET    /api/v1/municipios            # Lista
GET    /api/v1/municipios/{id}       # Perfil + estadísticas
GET    /api/v1/municipios/{id}/licitaciones

# Chatbot
POST   /api/v1/chat                  # Conversación con IA
GET    /api/v1/chat/history          # Historial

# Auth (Fase 2)
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/auth/me

# Alertas (Fase 2)
POST   /api/v1/alerts                # Crear alerta
GET    /api/v1/alerts                # Mis alertas
```

#### 3. Data Collection Service

**Scrapers programados:**
- Ejecución diaria/semanal con Celery
- Manejo de errores y reintentos
- Almacenamiento de logs

**Fuentes:**
1. **API CKAN (datos.gob.ar):** Prioritario, datos estructurados
2. **COMPR.AR:** Web scraping complementario
3. **CONTRAT.AR:** Web scraping complementario
4. **Portales provinciales:** Scraping selectivo (top 10 provincias)
5. **Portales municipales:** Scraping selectivo (grandes ciudades)

#### 4. Document Processing Service

**Pipeline:**
1. Descarga de PDFs/documentos
2. Detección de tipo (texto vs escaneado)
3. Extracción:
   - PyMuPDF para PDFs con texto
   - OCRmyPDF + Tesseract para escaneados
4. Normalización y limpieza
5. Almacenamiento en DB

#### 5. AI Analysis Service

**Capacidades:**

**a) Análisis de Licitación:**
- Extracción de requisitos clave
- Identificación de categorías/rubros
- Detección de montos y plazos
- Resumen automático

**b) Chatbot con RAG:**
- Vector database (ChromaDB) con licitaciones
- Embeddings de documentos
- Búsqueda semántica
- Generación de respuestas contextualizadas

**c) Insights de Municipios:**
- Análisis de patrones históricos
- Frecuencia de licitaciones por categoría
- Montos promedio
- Mejores épocas para aplicar

#### 6. Database Schema (PostgreSQL)

```sql
-- Tabla principal de licitaciones
CREATE TABLE licitaciones (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(500) NOT NULL,
    descripcion TEXT,
    organismo VARCHAR(200),
    municipio_id INTEGER REFERENCES municipios(id),
    categoria VARCHAR(100),
    monto_estimado DECIMAL(15,2),
    moneda VARCHAR(10),
    fecha_publicacion DATE,
    fecha_apertura DATE,
    fecha_cierre DATE,
    estado VARCHAR(50),
    url_oficial VARCHAR(500),
    documento_url VARCHAR(500),
    documento_texto TEXT,
    analisis_ia JSONB,
    fuente VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de municipios
CREATE TABLE municipios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    provincia VARCHAR(100),
    codigo_postal VARCHAR(20),
    poblacion INTEGER,
    presupuesto_anual DECIMAL(15,2),
    contacto JSONB,
    estadisticas JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de análisis con IA
CREATE TABLE licitacion_analysis (
    id SERIAL PRIMARY KEY,
    licitacion_id INTEGER REFERENCES licitaciones(id),
    requisitos_clave JSONB,
    requisitos_documentales JSONB,
    requisitos_tecnicos JSONB,
    requisitos_economicos JSONB,
    nivel_complejidad VARCHAR(50),
    recomendaciones TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de chat history (Fase 2)
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    messages JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_licitaciones_fecha ON licitaciones(fecha_publicacion DESC);
CREATE INDEX idx_licitaciones_municipio ON licitaciones(municipio_id);
CREATE INDEX idx_licitaciones_categoria ON licitaciones(categoria);
CREATE INDEX idx_licitaciones_estado ON licitaciones(estado);
CREATE INDEX idx_licitaciones_monto ON licitaciones(monto_estimado);
```

---

## 📝 Plan de Desarrollo

### Metodología

**Enfoque:** Agile/Scrum con sprints de 2 semanas
**MVP:** Versión mínima viable en 6-8 semanas
**Versión completa:** 12-16 semanas

### Principios de Desarrollo

1. **API First:** Diseñar API antes que UI
2. **Docker desde día 1:** Todo containerizado
3. **Tests automatizados:** Mínimo 70% coverage
4. **Documentación continua:** OpenAPI, README, comentarios
5. **Git flow:** Feature branches + PR reviews

---

## 🎯 Requisitos Mínimos (MVP)

### Funcionalidades Esenciales

#### Frontend MVP

✅ **Dashboard principal**
- Lista de licitaciones recientes (últimas 50)
- Estadísticas básicas (total, activas, cerradas)
- Búsqueda simple por texto

✅ **Página de detalle de licitación**
- Información completa
- Análisis básico con IA
- Link al documento original
- Botón "guardar" (localStorage)

✅ **Búsqueda y filtros**
- Filtro por categoría
- Filtro por municipio/provincia
- Filtro por rango de fechas
- Filtro por monto

✅ **Diseño responsive**
- Mobile-first
- Tablet y desktop optimizado

#### Backend MVP

✅ **API REST básica**
- CRUD de licitaciones
- Endpoints de búsqueda
- Endpoint de análisis IA

✅ **Integración con datos.gob.ar**
- Script de importación inicial
- Actualización diaria automática

✅ **Procesamiento de documentos**
- Descarga de PDFs
- Extracción de texto (solo PDFs con texto)
- OCR en fase 2

✅ **Análisis con IA (básico)**
- Resumen de licitación
- Extracción de requisitos principales
- Categorización automática

✅ **Base de datos**
- PostgreSQL con schema básico
- Migraciones con Alembic

#### DevOps MVP

✅ **Dockerización**
- Dockerfile frontend (multi-stage)
- Dockerfile backend
- docker-compose.yml para desarrollo
- docker-compose.prod.yml para producción

✅ **Scripts de deployment**
- Script de instalación en VPS
- Configuración de Nginx
- SSL con Certbot

### Fuera del MVP (Fase 2)

❌ Autenticación de usuarios
❌ Chatbot IA
❌ Análisis detallado de municipios
❌ Sistema de alertas por email
❌ OCR para documentos escaneados
❌ Scraping de portales provinciales
❌ API pública para terceros
❌ Panel de administración

---

## 🚀 Fases de Implementación

### Fase 0: Setup Inicial (Semana 1)

**Tareas:**
- [ ] Crear repositorio privado en GitHub
- [ ] Configurar estructura de monorepo o multi-repo
- [ ] Setup de entornos de desarrollo
- [ ] Configurar Docker base
- [ ] Definir convenciones de código
- [ ] Setup de pre-commit hooks

**Entregables:**
- Repositorio configurado
- README.md con instrucciones
- .gitignore, .dockerignore
- docker-compose.yml inicial

---

### Fase 1: Backend Base (Semanas 2-3)

**Tareas:**

**Semana 2:**
- [ ] Setup FastAPI con estructura modular
- [ ] Configurar PostgreSQL en Docker
- [ ] Implementar modelos de datos (SQLAlchemy)
- [ ] Crear migraciones con Alembic
- [ ] Endpoints básicos CRUD licitaciones
- [ ] Documentación automática (Swagger)

**Semana 3:**
- [ ] Integrar API de datos.gob.ar (CKAN)
- [ ] Script de importación inicial de datos
- [ ] Implementar paginación y filtros
- [ ] Tests unitarios básicos
- [ ] Docker build optimizado

**Entregables:**
- Backend API funcional
- Base de datos con datos reales
- Documentación OpenAPI
- Tests con >50% coverage

---

### Fase 2: Análisis con IA (Semana 4)

**Tareas:**
- [ ] Integrar OpenAI API
- [ ] Implementar descarga de documentos
- [ ] Procesamiento de PDFs con PyMuPDF
- [ ] Análisis de texto con GPT-4:
  - Resumen automático
  - Extracción de requisitos
  - Categorización
- [ ] Cache de resultados en Redis
- [ ] Endpoint `/licitaciones/{id}/analyze`
- [ ] Tests de integración

**Entregables:**
- Servicio de análisis IA funcional
- Documentos procesados y almacenados
- Análisis guardados en DB

---

### Fase 3: Frontend Base (Semanas 5-6)

**Tareas:**

**Semana 5:**
- [ ] Setup React + Vite + TypeScript
- [ ] Configurar UI library (MUI o Chakra)
- [ ] Implementar routing (React Router)
- [ ] Setup de state management
- [ ] Configurar API client (axios/fetch)
- [ ] Implementar Dashboard:
  - Lista de licitaciones
  - Cards responsive
  - Paginación
- [ ] Implementar búsqueda básica

**Semana 6:**
- [ ] Página de detalle de licitación
- [ ] Filtros avanzados (sidebar)
- [ ] Visualización de análisis IA
- [ ] Diseño responsive
- [ ] Dark/light mode
- [ ] Loading states y error handling
- [ ] Docker multi-stage build

**Entregables:**
- Frontend completo y funcional
- UI moderna y responsive
- Integración con backend
- Dockerfile optimizado

---

### Fase 4: Integration & Deployment (Semana 7)

**Tareas:**
- [ ] Integración frontend + backend
- [ ] Configurar Nginx como reverse proxy
- [ ] Setup docker-compose.prod.yml
- [ ] Scripts de deployment para VPS
- [ ] Configurar SSL/TLS (Let's Encrypt)
- [ ] Variables de entorno para producción
- [ ] Testing end-to-end
- [ ] Documentación de deployment
- [ ] Fix de bugs identificados

**Entregables:**
- Sistema completo integrado
- Documentación de instalación
- Scripts automatizados
- Listo para deployment

---

### Fase 5: Testing & MVP Launch (Semana 8)

**Tareas:**
- [ ] Testing exhaustivo de toda la aplicación
- [ ] Performance testing
- [ ] Security audit básico
- [ ] Optimización de queries de DB
- [ ] Ajustes de UI/UX
- [ ] Preparar datos de demo
- [ ] Deploy en VPS
- [ ] Monitoreo básico
- [ ] Documentación de usuario

**Entregables:**
- **MVP en producción** 🎉
- Documentación completa
- Video demo
- Métricas de performance

---

### Fase 6: Features Adicionales (Semanas 9-12)

**Prioridad Alta:**
- [ ] Sistema de autenticación (JWT)
- [ ] Registro e inicio de sesión
- [ ] Favoritos y guardados por usuario
- [ ] OCR para documentos escaneados
- [ ] Scraping de portales provinciales (top 5)
- [ ] Mejoras en análisis IA

**Prioridad Media:**
- [ ] Chatbot con RAG (LangChain + ChromaDB)
- [ ] Perfiles de municipios con estadísticas
- [ ] Sistema de alertas por email
- [ ] Dashboard de estadísticas avanzadas
- [ ] Exportación de datos (CSV, PDF)

**Prioridad Baja:**
- [ ] Panel de administración
- [ ] API pública con documentación
- [ ] Integración con calendarios
- [ ] Sistema de notificaciones push
- [ ] Mobile app (React Native)

---

### Fase 7: Optimización y Escalado (Semanas 13-16)

**Tareas:**
- [ ] Implementar caché agresivo
- [ ] Optimización de queries con índices
- [ ] Lazy loading y code splitting
- [ ] CDN para assets estáticos
- [ ] Rate limiting y throttling
- [ ] Monitoring con Prometheus + Grafana
- [ ] Logs centralizados
- [ ] Backup automático de DB
- [ ] CI/CD con GitHub Actions
- [ ] Tests de carga

**Entregables:**
- Sistema optimizado y escalable
- Monitoreo completo
- CI/CD automatizado
- Documentación técnica completa

---

## 💰 Estimaciones y Recursos

### Recursos Necesarios

#### Equipo Mínimo (MVP)

**Opción 1: Full-stack solo**
- 1 desarrollador full-stack senior
- Tiempo: 8 semanas full-time
- Skills: React, Python, FastAPI, Docker, PostgreSQL, IA/ML básico

**Opción 2: Equipo pequeño**
- 1 frontend developer (React)
- 1 backend developer (Python/FastAPI)
- Tiempo: 6 semanas
- Coordinación requerida

#### Costos de Infraestructura (Mensual)

**MVP (hasta 1000 usuarios):**
- VPS (4GB RAM, 2 CPU): $20-40/mes
- Dominio: $10-15/año
- OpenAI API: $50-100/mes (depende de uso)
- Total: ~$80-150/mes

**Escalado (hasta 10,000 usuarios):**
- VPS (8GB RAM, 4 CPU): $80-120/mes
- CDN (Cloudflare): Gratis/Pro $20
- OpenAI API: $200-500/mes
- Redis Cloud: $0-40/mes
- PostgreSQL managed: $0-50/mes (opcional)
- Total: ~$300-730/mes

#### Licencias de Software

- OpenAI API: Pay-as-you-go
- GitHub: Gratis (repo privado)
- Resto: Open source (gratis)

### Timeline Resumido

```
Semana 1:    [====] Setup inicial
Semana 2-3:  [========] Backend base
Semana 4:    [====] IA integration
Semana 5-6:  [========] Frontend
Semana 7:    [====] Integration & Deploy
Semana 8:    [====] Testing & MVP Launch 🚀
Semana 9-12: [============] Features adicionales
Semana 13-16:[============] Optimización
```

### Riesgos y Mitigaciones

**Riesgo 1: Cambios en estructura de portales**
- Mitigación: Priorizar API oficial (datos.gob.ar)
- Implementar alertas de scraping fallido

**Riesgo 2: Costos de OpenAI API**
- Mitigación: Caché agresivo, rate limiting
- Considerar modelos locales (Llama, Mistral) en fase 2

**Riesgo 3: Calidad de datos inconsistente**
- Mitigación: Validación y normalización robusta
- Marcar fuentes y confiabilidad

**Riesgo 4: Complejidad de deployment**
- Mitigación: Docker desde día 1
- Scripts automatizados

**Riesgo 5: Performance con volumen alto**
- Mitigación: Índices de DB, cache, paginación
- Arquitectura preparada para escalar

---

## 📋 Checklist de Inicio

Antes de empezar el desarrollo:

- [ ] Definir nombre del proyecto y dominio
- [ ] Crear repositorio privado en GitHub
- [ ] Obtener API key de OpenAI
- [ ] Confirmar presupuesto para infraestructura
- [ ] Verificar acceso a datos.gob.ar API
- [ ] Preparar entorno de desarrollo local
- [ ] Definir criterios de éxito del MVP
- [ ] Identificar usuarios beta para testing

---

## 🎯 Métricas de Éxito

### MVP Launch

- ✅ Al menos 1,000 licitaciones en base de datos
- ✅ 100% de licitaciones nacionales recientes
- ✅ Tiempo de respuesta API < 200ms (p95)
- ✅ Análisis IA funcional en 90% de documentos
- ✅ UI responsive en mobile/tablet/desktop
- ✅ Deploy exitoso en VPS
- ✅ Uptime > 95%

### Fase de Crecimiento (3 meses)

- 📈 10,000+ licitaciones indexadas
- 📈 100+ usuarios activos mensuales
- 📈 50+ licitaciones analizadas por IA diariamente
- 📈 Cobertura de 10+ provincias
- 📈 Feedback positivo de usuarios (NPS > 50)

---

## 📚 Recursos y Referencias

### Documentación Oficial

- **CKAN API**: https://docs.ckan.org/en/latest/api/
- **Open Contracting Data Standard**: https://standard.open-contracting.org/
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **Docker**: https://docs.docker.com/
- **Material UI**: https://mui.com/
- **LangChain**: https://python.langchain.com/

### Fuentes de Datos

- **Datos Argentina**: https://datos.gob.ar/dataset?tags=Contrataciones
- **COMPR.AR**: https://comprar.gob.ar/
- **CONTRAT.AR**: https://contratar.gob.ar/
- **ONC**: https://www.argentina.gob.ar/oficina-nacional-de-contrataciones

### Herramientas de Desarrollo

- **VS Code** con extensiones: Python, ESLint, Prettier, Docker
- **Postman** o **Insomnia** para testing de API
- **DBeaver** o **pgAdmin** para PostgreSQL
- **Docker Desktop** para desarrollo local

---

## 🏁 Conclusión

El mercado de licitaciones en Argentina presenta una oportunidad clara para un sistema moderno, inteligente y fácil de usar. Los competidores existentes tienen interfaces desactualizadas y carecen de capacidades avanzadas de IA.

**Nuestra propuesta diferenciadora:**
1. **Tecnología moderna**: React, FastAPI, Docker
2. **IA avanzada**: Análisis automático, chatbot inteligente
3. **Múltiples fuentes**: Nacional, provincial, municipal
4. **Fácil deployment**: Docker-ready para VPS
5. **Escalable**: Arquitectura preparada para crecer

**Próximos pasos:**
1. ✅ Investigación completada
2. ⏭️ Crear repositorio privado
3. ⏭️ Iniciar Fase 0: Setup inicial
4. ⏭️ Comenzar desarrollo del MVP

---

**Documento preparado el:** 13 de Noviembre de 2025
**Última actualización:** 13 de Noviembre de 2025
**Versión:** 1.0
