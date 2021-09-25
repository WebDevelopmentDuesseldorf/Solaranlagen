import React, { useContext, useState, useEffect } from 'react'
import { auth } from "../../firebase"


const AuthContext = React.createContext()


export const useAuth = () => useContext(AuthContext)


export const AuthProvider = ({children}) => {
    const [currentUser, setCurrentUser] = useState()
    const [loading, setLoading ] = useState(true)

    const signup = (email, password) => auth.createUserWithEmailAndPassword(email, password)

    const login = (email, password) => auth.signInWithEmailAndPassword(email, password)

    const logout = () => auth.signOut() 

    const resetPassword = (email) => auth.sendPasswordResetEmail(email)
    
    const updateEmail = (email) => currentUser.updateEmail(email)
    
    const updatePassword = (password) => currentUser.updatePassword(password)

    useEffect(()=> {
       const unsubscribe =  auth.onAuthStateChanged(user => {
        setLoading(false)    
        setCurrentUser(user)
        })

        return unsubscribe 
        // eslint-disable-next-line

    }, [])
    

    const value = {
        currentUser, 
        login,
        logout,
        signup,
        resetPassword,
        updateEmail,
        updatePassword
    }

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    )
}