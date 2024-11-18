'use client'

import axios from 'axios';

export async function registerUser(formValues) {
  try {
    const response = await axios.post('http://localhost:8000/register', formValues, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    return { success: true, data: response.data };
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return { success: false, error: error.response.data };
    }
    return { success: false, error: 'An unexpected error occurred' };
  }
}


export async function loginUser(formValues) {
  try {
    const response = await axios.post('http://localhost:8000/login', formValues);
    sessionStorage.setItem('access_token', response.data.access_token)
    sessionStorage.setItem('userGroup', response.data.userGroup)
    sessionStorage.setItem('userName', response.data.userName)
    return { success: true, data: response.data };
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return { success: false, error: error.response.data };
    }
    return { success: false, error: 'An unexpected error occurred' };
  }
}