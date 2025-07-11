# Guida Operazioni Classificate - Merrywinter Security Consulting

## 🔒 Nuove Funzionalità [CLASSIFIED]

### ✅ **Comandi Aggiornati con Opzione Classificata:**

#### 1. **Deployment Classificati**
```
/deployment sector:alpha units:5 mission_type:reconnaissance priority:high classified:True
```

**Risultato:**
- **Titolo**: `🚁 [CLASSIFIED] DEPLOYMENT AUTHORIZATION`
- **Autorizzazione**: `authorized by: [RESTRICTED]`
- **Nota**: `🔒 CLASSIFIED OPERATION - Access restricted to Executive Command personnel only`

#### 2. **Operazioni Classificate**
```
/operation_start operation_name:"Operation Silent Storm" objective:"Secure intelligence assets" participants:3 duration:6 classified:True
```

**Risultato:**
- **Titolo**: `🎯 [CLASSIFIED] OPERATION COMMENCED`
- **Comandante**: `authorized by: [RESTRICTED]`
- **Nota**: `🔒 CLASSIFIED OPERATION - Access restricted to Executive Command personnel only`

#### 3. **Missioni Classificate**
```
!mission reconnaissance classified:True
```

**Risultato:**
- **Titolo**: `🎯 [CLASSIFIED] MISSION BRIEFING - RECONNAISSANCE`
- **Operatore**: `authorized by: [RESTRICTED]`
- **Nota**: `🔒 CLASSIFIED MISSION - Access restricted to BETA+ clearance only`

## 🎯 **Permessi e Controlli di Sicurezza**

### **Deployment Classificati:**
- **Richiede**: Director+ clearance (normale)
- **Classificato**: Solo Executive Command può autorizzare
- **Errore**: "❌ Only Executive Command can authorize classified operations."

### **Operazioni Classificate:**
- **Richiede**: Chief+ clearance (normale)
- **Classificato**: Solo Executive Command può autorizzare
- **Errore**: "❌ Only Executive Command can authorize classified operations."

### **Missioni Classificate:**
- **Richiede**: Military clearance (normale)
- **Classificato**: Solo BETA+ clearance può accedere
- **Errore**: "❌ You need BETA+ clearance to access classified missions."

## 🔐 **Formato Messaggi Classificati**

### **Schema Standard:**
```
🚁 [CLASSIFIED] DEPLOYMENT AUTHORIZATION

Deployment ID: DEP-12345
authorized by: [RESTRICTED]
Clearance Level: EXECUTIVE_COMMAND
Timestamp: 2025-07-11 21:40:00 UTC

🔒 CLASSIFIED OPERATION
Access restricted to Executive Command personnel only

[resto del messaggio normale]
```

### **Differenze con Operazioni Normali:**
- **Normale**: `Authorized By: @username`
- **Classificato**: `authorized by: [RESTRICTED]`

- **Normale**: `🚁 DEPLOYMENT AUTHORIZATION`
- **Classificato**: `🚁 [CLASSIFIED] DEPLOYMENT AUTHORIZATION`

## 📊 **Dati Salvati**

Tutti i deployment, operazioni e missioni classificate vengono salvati con:
```json
{
  "deployment_id": "DEP-12345",
  "classified": true,
  "authorized_by": 123456789,
  "timestamp": "2025-07-11T21:40:00Z"
}
```

## 🎖️ **Gerarchia Accesso**

### **Executive Command** (Livello 10):
- Può autorizzare TUTTI i deployment e operazioni classificate
- Accesso completo a tutte le funzionalità

### **Department Directors** (Livello 8):
- Possono fare deployment normali
- NON possono autorizzare operazioni classificate

### **BETA+ Clearance**:
- Possono accedere a missioni classificate
- Limitato a briefing, non autorizzazioni operative

### **ALPHA Clearance**:
- Solo operazioni normali
- Nessun accesso a materiale classificato

Il sistema ora supporta completamente operazioni classificate con controlli di sicurezza adeguati e formato messaggi standardizzato [RESTRICTED].