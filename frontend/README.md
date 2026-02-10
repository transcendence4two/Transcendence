# Transcendence - Frontend

Game application developed with React, TypeScript, Vite and Tailwind CSS v4.

## 📋 Requirements

Before you begin, make sure you have installed:

- **Bun** >= 1.0 (or **Node.js** >= 18.0.0)
- **Git**

### Installing Bun

```bash
# macOS/Linux
curl -fsSL https://bun.sh/install | bash

# Windows (via WSL)
curl -fsSL https://bun.sh/install | bash
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Transcendence/frontend
```

2. Install dependencies:
```bash
bun install
```

## 💻 Running the Project

### Development Mode
```bash
bun run dev
```
The application will be available at `http://localhost:5173`

### Production Build
```bash
bun run build
```

### Build Preview
```bash
bun run preview
```

### Linting
```bash
bun run lint
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── assets/           # Images and static resources
│   ├── components/
│   │   ├── common/       # Reusable components (Button, Card)
│   │   ├── home/         # Home-specific components (HeroSection)
│   │   ├── icons/        # SVG icon components
│   │   └── layout/       # Layout components (Header, Footer)
│   ├── pages/            # Application pages
│   ├── styles/           # Global styles
│   │   └── index.css     # Tailwind styles + custom classes
│   ├── App.tsx           # Main component
│   └── main.tsx          # Entry point
├── public/               # Public files
├── index.html
├── package.json
├── vite.config.ts
└── tailwind.config.ts
```

## 🛠️ Technologies Used

- **React 19** - Library for building user interfaces
- **TypeScript** - JavaScript superset with static typing
- **Vite** - Build tool and dev server
- **Tailwind CSS v4** - Utility-first CSS framework
- **React Router DOM** - Page routing
- **Bun** - Runtime and package manager

## 🎨 Styles and Themes

The project uses Tailwind CSS v4 with:
- Inline utility classes for simple layouts
- Custom classes in `index.css` for reusable components
- Support for **dark mode** and **light mode**
- Custom gradients and animations

### Switching Themes
Click on the 🌞/🌙 icon in the top right corner of the header to switch between dark and light mode.

## 📦 Available Scripts

| Script | Description |
|--------|-----------|
| `bun run dev` | Starts the development server |
| `bun run build` | Creates the production build |
| `bun run preview` | Preview the production build |
| `bun run lint` | Runs ESLint |

## 🔧 Additional Configuration

### Recommended VS Code Extensions
- **Tailwind CSS IntelliSense** - Autocomplete for Tailwind classes
- **ESLint** - Real-time linting
- **Prettier** - Code formatting

### VS Code Settings
Add to `.vscode/settings.json`:
```json
{
  "css.lint.unknownAtRules": "ignore",
  "editor.formatOnSave": true
}
```

## 📝 Code Conventions

- **Components**: PascalCase (e.g. `Button.tsx`, `HeroSection.tsx`)
- **Utility files**: camelCase
- **Custom CSS classes**: kebab-case (e.g. `.btn-hero`, `.card-feature`)
- **Component props**: Interfaces with `Props` suffix (e.g. `ButtonProps`)

## 🤝 Contributing

1. Create a branch for your feature (`git checkout -b feature/new-feature`)
2. Commit your changes (`git commit -m 'Add new feature'`)
3. Push to the branch (`git push origin feature/new-feature`)
4. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

---

**Developed by** Transcendence 42 Rio C2G1 © 2026

