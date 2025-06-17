# MCP Tool Ideas

## User Identification Tool
**Status**: Requires investigation
**Complexity**: High
**Dependencies**: Internal auth system

### Concept
A tool that allows the MCP server to identify the current user, enabling:
- Personalized responses
- Access control
- User-specific operations

### Current Understanding
- Browser certificate authentication at ingress
- JWT tokens for internal service auth
- Internal API to resolve user info from passnumber

### Questions to Investigate
1. How does the MCP server receive auth information?
   - Does it see the original certificate?
   - Does it receive a JWT?
   - Where in the request chain is it positioned?

2. What user information is available?
   - What user details can we access?

3. Security considerations
   - How to securely handle user info?
   - What permissions are needed?
   - How to prevent unauthorized access?

### Next Steps
1. Investigate auth flow at work
2. Map out service interactions
3. Identify where user info can be obtained
4. Design secure implementation

---
### Jira Client (carrying users credentials)
- Create/update tickets
- Search tickets
- Get ticket details
- Add comments
- Update status

---
### Mattermost Client (carrying users credentials)
- Send messages
- Create posts
- Read channels
- Search messages
- Handle reactions

---
### Confluence Client (carrying users credentials)
- Read pages
- Search content

---
### Outlook Client
- Read emails
- Send emails
- Search messages
- Handle attachments
- Manage calendar

---
### Image Generation
- Generate images from text descriptions
- Support different styles and parameters
- Handle image storage and retrieval
- Support image editing/modification
- Manage generation quotas/limits

---
### Mermaid Chart Renderer
- Render Mermaid syntax to images
- Support all Mermaid diagram types:
  - Flowcharts
  - Sequence diagrams
  - Class diagrams
  - State diagrams
  - Entity Relationship diagrams
  - User Journey diagrams
- Customize theme and style
- Export to different formats (PNG, SVG)
- Handle large/complex diagrams

---
### Kubernetes Query Tool
- Query pod status and logs
- Check for common error patterns
- Monitor resource usage
- Track deployment status
- Check service health
- Query events and warnings
- Support multiple clusters
- Handle RBAC permissions

---
### Network Information
**Specific Use Case**: Service Health Checks
- When an MCP client tool fails to respond
- Check if the target service is reachable
- Help diagnose network vs service issues
- Example: Jira client fails → check if Jira is reachable

---
### GitLab Integration
- Create/update merge requests
- Review and comment on code
- Trigger CI/CD pipelines
- Monitor pipeline status
- Search repositories and code
- Handle repository operations:
  - Create branches
  - Create/update issues
  - Manage labels and milestones
  - Handle merge conflicts
- Access project documentation
- Track project metrics and analytics
- Support multiple GitLab instances
- Handle authentication and permissions
- Integrate with existing review workflows

---
### Markdown to PDF Converter
- Convert markdown text to PDF documents
- Support for:
  - Code syntax highlighting
  - Tables
  - Page numbers and headers/footers (marking header and footer)
- Handle binary data flow:
  - Generate PDF
- Features:
  - Metadata support (title, author (pulled from certificate), date (fetched from datetime mcp))
  - Watermarking options (AI GENERATED)
- PDF Storage and Serving:
  - Use MinIO for ephemeral storage
  - Generate pre-signed URLs for downloads
  - Configure 24-hour lifecycle rules for automatic cleanup
  - Serve through existing proxy at artifacts.contesso.net
  - Handle download tracking for immediate cleanup when possible
  - Ensure proper CORS and security headers
  - Support for large file downloads
  - Error handling for failed conversions or downloads

---
### API Documentation and Discovery
- Leverage FastAPI's built-in OpenAPI documentation
- Features:
  - Automatic OpenAPI schema generation
  - Interactive Swagger UI (/docs)
  - ReDoc alternative view (/redoc)
  - Authentication scheme documentation
  - Request/response models
  - Query parameters and path variables
  - Example values and schemas
- Enhancements:
  - Custom documentation templates
  - Additional examples beyond FastAPI defaults
  - Environment-specific endpoint documentation
  - Rate limit and quota information
  - Common error responses
  - Versioning strategy documentation
- Integration:
  - Service registry integration
  - API gateway synchronization
  - Documentation aggregation
- Developer Experience:
  - Code snippet generation for common languages
  - Authentication flow examples
  - Environment setup guides
  - Common patterns and best practices
- Security:
  - Access control for sensitive endpoints
  - Internal-only documentation
  - Audit logging of documentation access
- Maintenance:
  - Automated schema validation
  - Version tracking
  - Deprecation notices
  - Migration guides
  ---

  already existing, but interesting ones
  https://github.com/ChanMeng666/server-google-news
  https://github.com/Shy2593666979/mcp-server-email
  https://github.com/QuantGeekDev/docker-mcp
  https://github.com/githejie/mcp-server-calculator
  https://github.com/oschina/mcp-gitee
  https://github.com/Flux159/mcp-server-kubernetes