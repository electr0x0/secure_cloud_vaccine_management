'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'


export function withAuth(WrappedComponent) {
  return function AuthenticatedComponent(props) {
    const router = useRouter()

    useEffect(() => {
      const token = sessionStorage.getItem('token')
      if (!token) {
        router.push('/login')
      }
    }, [router])

    return <WrappedComponent {...props} />;
  };
}