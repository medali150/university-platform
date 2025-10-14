import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const publicPaths = ['/login', '/register', '/']
const protectedPaths = ['/dashboard', '/messages', '/absences', '/subjects', '/makeups']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Allow public paths
  if (publicPaths.some(path => pathname.startsWith(path))) {
    return NextResponse.next()
  }

  // Check for protected paths
  if (protectedPaths.some(path => pathname.startsWith(path))) {
    // Check multiple possible token locations for compatibility
    const token = request.cookies.get('authToken')?.value || 
                  request.cookies.get('accessToken')?.value ||
                  request.headers.get('authorization')?.replace('Bearer ', '')

    if (!token) {
      // For now, allow through - let client-side auth handle it
      // This prevents middleware redirect loops during SSR
      return NextResponse.next()
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}