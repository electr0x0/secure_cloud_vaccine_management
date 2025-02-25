import { useState, useEffect } from 'react'
import axios from 'axios'

export function useVaccinationData() {
  const [vaccinationData, setVaccinationData] = useState(null)

  const fetchVaccinationHistory = async (email: string) => {
    const API = process.env.NEXT_PUBLIC_API_URL
    try {
      const response = await axios.post(`${API}/api/vaccination-history`, { email })
      return response.data
    } catch (error) {
      console.error('Error fetching vaccination history:', error)
      throw error
    }
  }

  useEffect(() => {
    const userEmail = sessionStorage.getItem('user_email')
    if (userEmail) {
      fetchVaccinationHistory(userEmail)
        .then(setVaccinationData)
        .catch(console.error)
    }
  }, [])

  return { vaccinationData, setVaccinationData, fetchVaccinationHistory }
}

