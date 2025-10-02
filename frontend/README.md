# University Management Platform - Frontend

A modern, production-ready frontend for a comprehensive University Management Platform built with Next.js 14, TypeScript, and Tailwind CSS.

## 🚀 Features

### Role-Based Dashboards
- **Student Dashboard**: View timetable, justify absences, send messages
- **Teacher Dashboard**: Manage classes, mark absences, propose make-up sessions
- **Department Head Dashboard**: Full timetable management, analytics, user management

### Core Functionality
- 🔐 **JWT Authentication** with automatic token refresh
- 📅 **Interactive Timetable Grid** with drag-and-drop editing
- 📊 **Analytics Dashboard** with charts and reporting
- 💬 **Real-time Messaging** system
- 📝 **Absence Management** with justification uploads
- 🔄 **Make-up Session** proposals and approvals
- 📑 **PDF/ICS Export** for timetables
- 🎨 **Dark/Light Theme** support

### Technical Features
- ⚡ **Server-Side Rendering** with Next.js 14 App Router
- 🔄 **Optimistic Updates** with React Query
- 📱 **Responsive Design** with Tailwind CSS
- ♿ **Accessibility** WCAG AA compliant
- 🧪 **Type Safety** with TypeScript strict mode
- 🎨 **Modern UI** with shadcn/ui components

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: React Query (TanStack Query)
- **Forms**: React Hook Form + Zod validation
- **Authentication**: JWT with httpOnly cookies
- **Icons**: Lucide React
- **Date Handling**: date-fns
- **Charts**: Recharts
- **Notifications**: Sonner

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env.local
   ```

   Configure your environment variables:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   TOKEN_REFRESH_MARGIN_MS=60000
   ```

4. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

5. **Open in browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🏗️ Build & Deploy

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm run start
```

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
```

### Testing
```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e
```

## 🎯 Role-Based Access

The application automatically redirects users based on their roles:

- **STUDENT** → `/dashboard/student`
- **TEACHER** → `/dashboard/teacher`
- **DEPARTMENT_HEAD** → `/dashboard/department-head`

### Authentication Flow
1. User visits `/login`
2. Enters credentials
3. JWT tokens stored securely
4. Automatic redirect to role-specific dashboard
5. Protected routes enforced by middleware

## 📁 Project Structure

```
frontend/
├── app/                          # Next.js 14 App Router
│   ├── dashboard/               # Role-based dashboards
│   │   ├── student/
│   │   ├── teacher/
│   │   └── department-head/
│   ├── login/                   # Authentication
│   ├── messages/                # Messaging system
│   ├── absences/                # Absence management
│   ├── subjects/                # Subject CRUD
│   └── makeups/                 # Make-up sessions
├── components/                   # Reusable components
│   ├── auth/                    # Authentication components
│   ├── layout/                  # Layout components
│   ├── timetable/               # Timetable components
│   ├── analytics/               # Analytics components
│   ├── forms/                   # Form components
│   └── ui/                      # shadcn/ui components
├── hooks/                       # Custom React hooks
├── lib/                         # Utility libraries
│   ├── api.ts                   # API client
│   ├── auth.ts                  # Authentication service
│   ├── timetable.ts             # Timetable utilities
│   └── roles.ts                 # Role management
├── types/                       # TypeScript definitions
└── styles/                      # Global styles
```

## 🔧 Key Components

### TimetableGrid
Interactive timetable with editing capabilities:
- Click empty cells to create sessions
- Click existing sessions to edit/delete
- Merge consecutive sessions automatically
- Color-coded by subject
- Export to PDF/ICS

### SessionFormDialog
Modal form for creating/editing sessions:
- Subject, group, room selection
- Date and time pickers
- Status management (Planned/Makeup/Cancelled)
- Validation with Zod

### RoleGuard
Protects routes based on user roles:
- Automatic redirects
- Loading states
- Error handling

## 🎨 Theming

The application supports both light and dark themes:
- Automatic system detection
- Manual toggle in header
- Persistent preference storage
- Tailwind CSS custom properties

## 📊 Analytics Dashboard

Department heads have access to:
- Absence rate charts by group
- Room utilization metrics
- Subject coverage reports
- Export capabilities

### Extending Charts
To add new chart types:
1. Create component in `components/analytics/`
2. Add data fetching with React Query
3. Use Recharts for visualization
4. Add to dashboard layout

## 💬 Real-time Features

### WebSocket Integration (Prepared)
The messaging system is prepared for WebSocket integration:
```typescript
// In components/messages/MessageThread.tsx
// TODO: Replace polling with WebSocket connection
useEffect(() => {
  // const socket = io(process.env.NEXT_PUBLIC_WS_URL)
  // socket.on('message', handleNewMessage)
  // return () => socket.disconnect()
}, [])
```

## 🧪 Testing

### Unit Tests
Located in `tests/unit/`:
- Component rendering tests
- Utility function tests
- Hook behavior tests

### E2E Tests
Located in `tests/e2e/`:
- Login flow
- Timetable interactions
- Role-based navigation

Example test structure:
```typescript
// tests/e2e/login.spec.ts
test('should login and redirect based on role', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[data-testid=email]', 'student@test.com')
  await page.fill('[data-testid=password]', 'password')
  await page.click('[data-testid=submit]')
  await expect(page).toHaveURL('/dashboard/student')
})
```

## 🔐 Security

- JWT tokens with automatic refresh
- Protected routes with middleware
- XSS protection with CSP headers
- CSRF protection built-in
- Input validation with Zod
- Role-based access control

## 🚀 Performance

- Server-side rendering with Next.js
- Automatic code splitting
- Image optimization
- Caching with React Query
- Optimistic updates
- Lazy loading of components

## 📱 Mobile Support

- Responsive design with Tailwind
- Touch-friendly interactions
- Collapsible sidebar
- Mobile-first approach

## 🌐 Internationalization (Prepared)

The codebase is prepared for i18n:
- Text extraction ready
- Date formatting with locale support
- RTL layout support in Tailwind

## 🔧 Development Tips

### Adding New Routes
1. Create page in `app/` directory
2. Add to sidebar navigation
3. Update role permissions in `lib/roles.ts`
4. Add route protection if needed

### Custom Hooks
Use React Query for data fetching:
```typescript
function useSubjects() {
  return useQuery({
    queryKey: ['subjects'],
    queryFn: () => api.getSubjects(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}
```

### Form Validation
Use Zod schemas with React Hook Form:
```typescript
const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email'),
})

const form = useForm({
  resolver: zodResolver(schema),
})
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing code style
4. Add tests for new features
5. Update documentation
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with details
4. Include browser/OS information

---

Built with ❤️ using Next.js 14, TypeScript, and Tailwind CSS.