# Guida Sistema Ticket - Merrywinter Security Consulting

## Nuove Funzionalità Aggiunte

### 🎫 Stati Ticket Disponibili
1. **🟢 Open** - Appena creato
2. **🟡 Taken** - Preso in carico da staff
3. **🔵 In Progress** - In lavorazione
4. **🟠 Pending Review** - In attesa di revisione
5. **🔴 Closed** - Completato/Risolto
6. **⚫ Auto Closed** - Chiuso automaticamente

### 📋 Comandi Ticket

#### Per Utenti:
- `/report-operator` - Segnala operatore
- `/commission` - Richiedi servizio PMC
- `/tech-issue` - Segnala problema tecnico
- `/ticket-status <ticket_id>` - Controlla stato ticket

#### Per Staff (Moderatori+):
- `/update-ticket <ticket_id> <status>` - Aggiorna stato ticket
- `/close-ticket <ticket_id>` - Chiudi ticket
- `/ticket-status <ticket_id>` - Controlla stato ticket

## Workflow Commission

### 1. Creazione Commission
```
/commission service_details:"Descrizione del servizio richiesto"
```

### 2. Gestione Staff
```
/update-ticket e55aeb6b-ba24-429a-94d5-4951a76238d3 taken
```
- Il ticket passa da "Open" a "Taken"
- Viene notificato nel canale del ticket

### 3. Avanzamento Lavoro
```
/update-ticket e55aeb6b-ba24-429a-94d5-4951a76238d3 in_progress
```
- Indica che il lavoro è iniziato

### 4. Revisione
```
/update-ticket e55aeb6b-ba24-429a-94d5-4951a76238d3 pending_review
```
- Pronto per controllo finale

### 5. Completamento
```
/close-ticket e55aeb6b-ba24-429a-94d5-4951a76238d3
```
- Ticket chiuso, canale eliminato dopo 5 minuti

## Correzioni Implementate

### 🔧 Nomi Canali Corti
- **Prima**: `ticket-commission-username-ticket_id`
- **Dopo**: `ticket-commission-12345678` (massimo 95 caratteri)
- **Fallback**: `tkt-commission-12345678` se troppo lungo

### 🎯 Ticket Esistente
Per il ticket commission esistente:
- **ID**: `e55aeb6b-ba24-429a-94d5-4951a76238d3`
- **Comando**: `/update-ticket e55aeb6b-ba24-429a-94d5-4951a76238d3 taken`

## Permessi

### Chi può aggiornare ticket:
- **Moderatori** (Department Directors)
- **Admin** (Executive Command, Board of Directors)
- **BETA** clearance o superiore
- **Community Managers**

### Notifiche Automatiche:
- Ogni cambio di stato viene notificato nel canale del ticket
- Include timestamp, utente che ha fatto il cambio, e nuovo stato
- Colori diversi per ogni stato

## Esempio Pratico

```
1. Cliente: /commission "Scorta VIP per evento aziendale"
2. Staff: /update-ticket abc123 taken
3. Staff: /update-ticket abc123 in_progress
4. Staff: /update-ticket abc123 pending_review
5. Admin: /close-ticket abc123
```

Il sistema ora supporta un workflow completo per la gestione delle commission e altri ticket, con stati intermedi e notifiche automatiche.