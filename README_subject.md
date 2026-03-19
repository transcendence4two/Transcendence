This project has been created as part of the 42 curriculum by [aldantas](https://profile-v3.intra.42.fr/users/aldantas), [dbessa](https://profile-v3.intra.42.fr/users/dbessa), [jveras](https://profile-v3.intra.42.fr/users/jveras), [lraggio](https://profile-v3.intra.42.fr/users/lraggio) e [marcribe](https://profile-v3.intra.42.fr/users/marcribe)

# Description
## Tic Tac Infinity
This section have to clearly presents the project, its goal and brief overview.

# Instructions
- Any relevant information about compilation, installation and/or execution
- Prerequisites needed (software tools, versions, configuration like .env setup, etc.) and step-by-step instructions to run the project

# Resources

# Team Information
### aldantas
```
Roles
- Tech Lead
- Developer

Responsabilities
- Resp1
- Resp2
```

### dbessa
```
Roles
- Project Manager
- Developer

Responsabilities
- Resp1
- Resp2
```

### jveras
```
Role
- Developer

Responsabilities
- Resp1
- Resp2
```

### lraggio
```
Roles
- Product Owner
- Developer

Responsabilities
- Resp1
- Resp2
```

### marcribe
```
Role
- Developer

Responsabilities
- Resp1
- Resp2
```

# Project Management
How the team organized the work (task distribution, meetings, etc.).
Tools used for project management (GitHub Issues, Trello, etc.).
Communication channels used (Discord, Slack, etc.).

# Technical Stack
Frontend technologies and frameworks used.
Backend technologies and frameworks used.
Database system and why it was chosen.
Any other significant technologies or libraries.
Justification for major technical choices.

# Database Schema
Visual representation or description of the database structure.
Tables/collections and their relationships.
Key fields and data types.

# Feature list
Complete list of implemented features.
Which team member(s) worked on each feature.
Brief description of each feature’s functionality.

# Modules

```
Major: Use a framework for both the frontend and backend.
◦ Use a frontend framework (React, Vue, Angular, Svelte, etc.).
◦ Use a backend framework (Express, NestJS, Django, Flask, Ruby on Rails, etc.).
◦ Full-stack frameworks (Next.js, Nuxt.js, SvelteKit) count as both if you use both their frontend and backend capabilities.
```
Why this module?

R: `To faster development using well-knwon and tested market frameworks`

How it was implemented?

R: `In frontend we've used React and for backend we've used Java Quarkus for friends-service, Mix for email-service and Python FastAPI for tournament-service and usermanagement-service`

Who implemented?

R: `Front end was implemented by both dbessa and jveras, while Backend was implemented by aldantas, lraggio and marcribe. All the integrations was made by the team`

***

```
Major: Implement real-time features using WebSockets or similar technology.
◦ Real-time updates across clients.
◦ Handle connection/disconnection gracefully.
◦ Efficient message broadcasting.
```
Why this module?

R: `|`

How it was implemented?

R: `|`

Who implemented?

R: `|`

***

```
Major: A public API to interact with the database with a secured API key, rate
limiting, documentation, and at least 5 endpoints:
◦ GET /api/{something}
◦ POST /api/{something}
◦ PUT /api/{something}
◦ DELETE /api/{something}
```
Why this module?

R: `|`

How it was implemented?

R: `|`

Who implemented?

R: `|`

***

```
Minor: Use an ORM for the database.
```
Why this module?

R: `|`

How it was implemented?

R: `|`

Who implemented?

R: `|`


***

```
Major: Standard user management and authentication.
◦ Users can update their profile information.
◦ Users can upload an avatar (with a default avatar if none provided).
◦ Users can add other users as friends and see their online status.
◦ Users have a profile page displaying their information.
```
Why this module?

R: `|`

How it was implemented?

R: `|`

Who implemented?

R: `|`


***

```
Minor: Implement remote authentication with OAuth 2.0 (Google, GitHub, 42, etc.).
```
Why this module?

R: `|`

How it was implemented?

R: `|`

Who implemented?

R: `|`


***

```
Minor: Implement a complete 2FA (Two-Factor Authentication) system for the users.
```
Why this module?

R: `|`

How it was implemented?

R: `|`

Who implemented?

R: `|`

***

```
Major: Implement a complete web-based game where users can play against each other.
◦ The game can be real-time multiplayer (e.g., Pong, Chess, Tic-Tac-Toe, Card games, etc.).
◦ Players must be able to play live matches.
◦ The game must have clear rules and win/loss conditions.
◦ The game can be 2D or 3D.
```
Why this module?

R: `|`

How it was implemented?

R: `|`

Who implemented?

R: `|`

***

```
Major: Remote players — Enable two players on separate computers to play the
same game in real-time.
◦ Handle network latency and disconnections gracefully.
◦ Provide a smooth user experience for remote gameplay.
◦ Implement reconnection logic.
```
Why this module?

R: `|`

How it was implemented?

R: `|`

Who implemented?

R: `|`

***

```
Major: Infrastructure for log management using ELK (Elasticsearch, Logstash,
Kibana).
◦ Elasticsearch to store and index logs.
◦ Logstash to collect and transform logs.
◦ Kibana for visualization and dashboards.
◦ Implement log retention and archiving policies.
◦ Secure access to all components.
```
Why this module?

R: `|`

How it was implemented?

R: `|`

Who implemented?

R: `|`

***

```
Major: Monitoring system with Prometheus and Grafana.
◦ Set up Prometheus to collect metrics.
◦ Configure exporters and integrations.
◦ Create custom Grafana dashboards.
◦ Set up alerting rules.
◦ Secure access to Grafana.
```
Why this module?

R: `|`

How it was implemented?

R: `|`

Who implemented?

R: `|`

***

```
Major: Backend as microservices.
◦ Design loosely-coupled services with clear interfaces.
◦ Use REST APIs or message queues for communication.
◦ Each service should have a single responsibility.
```
Why this module?

R: `|`

How it was implemented?

R: `|`

Who implemented?

R: `|`

***

```
Minor: Support for additional browsers.
◦ Full compatibility with at least 2 additional browsers (Firefox, Safari, Edge, etc.).
◦ Test and fix all features in each browser.
◦ Document any browser-specific limitations.
◦ Consistent UI/UX across all supported browsers.
```
Why this module?

R: `|`

How it was implemented?

R: `|`

Who implemented?

R: `|`

***

```
Minor: Custom-made design system with reusable components, including a proper
color palette, typography, and icons (minimum: 10 reusable components).
```
Why this module?

R: `|`

How it was implemented?

R: `|`

Who implemented?

R: `|`

***

```
Points calculation
2 + 2 + 2 + 1 + 2 + 1 + 1 + 2 + 2 + 2 + 2 + 2 + 1 + 1 = 23
```

Justification for each module choice, especially for custom "Modules of choice".
How each module was implemented.
Which team member(s) worked on each module.

# Individual Contributions
Detailed breakdown of what each team member contributed.

Specific features, modules, or components implemented by each person.
Any challenges faced and how they were overcome.
