def levison_durbin(r,M):
    """Linear prediction coeffiecients estimated by Levinson-Durbin algorithm
    Input
    r: auto correlation vector with lag varying from 0 to M
    M: order of prediction coefficients"""
    
    # 
    if r.shape[0]<M+1:
        raise Exception('the length of r should be at least 1 larger than M')
    
    #correlation vector, lag vary from 1 to M
    r_vect = r[1:]
    
    # coeffficients of error filter 
    a = np.zeros((M+1,1))
    a[0] = 1 
    
    if M <0:
        return 0
    
    # when m=1
    P_m_1 = r[0] # the mean suqare error of (m-1)th predictor, P_0 = r(0) 
    Delta_m_1 = r_vect[0]
    k_m = -Delta_m_1/P_m_1# reflection coefficients
    a[1] = k_m
    P_m = P_m_1*(1-k_m**2)
    
    if M==1:
        return [a,P_m]
    
    a_aug = np.zeros((M+1,1)) # for convinience, explained in following
    
    for m in xrange(2,M+1):
        P_m_1 = P_m
        
        a_m_1 = a[:m] # coefficient of (m-1)_th order

        Delta_m_1 = np.dot(np.flipud(r_vect[:m]).T,a_m_1)

        k_m = -Delta_m_1/P_m_1
        
        a_aug[:m]=a[:m] # equivilent to concatenate 0 to the end of a_m_1
        a[:m+1] = a_aug[:m+1] + k_m*np.flipud(np.conj(a_aug[:m+1]))
        P_m = P_m_1*(1-k_m**2)
    return [a,P_m]