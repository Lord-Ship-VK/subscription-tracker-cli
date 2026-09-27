# SmartSub: UML Diagrams

## Use Case Diagram

```mermaid
usecaseDiagram
    actor User
    
    usecase "Add Subscription" as UC1
    usecase "List Subscriptions" as UC2
    usecase "Update Subscription" as UC3
    usecase "Delete Subscription" as UC4
    usecase "View Analytics" as UC5
    usecase "Check Alerts" as UC6
    usecase "Calculate Savings" as UC7
    usecase "Search Subscriptions" as UC8
    usecase "Export CSV" as UC9
    
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    User --> UC8
    User --> UC9
```

## Class Diagram

*Note: SmartSub utilizes a procedural design relying on simple data classes rather than deep object-oriented inheritance.*

```mermaid
classDiagram
    class Subscription {
        +int sub_id
        +str name
        +float cost
        +str cycle
        +str next_date
        +str category
        +to_dict() dict
        +from_dict(dict) Subscription$
    }

    class storage {
        +str DATA_FILE
        +load_data() list[Subscription]
        +save_data(list[Subscription])
        +set_data_file(str)
    }

    class utils {
        +validate_name(str) str
        +validate_cost(float) float
        +validate_date(str) str
        +validate_category(str) str
        +refresh_renewal_dates(list[Subscription]) bool
        +advance_renewal_date(str, str, date) str
        -_add_months(date, int) date
        -_add_years(date, int) date
    }

    class manager {
        +add_subscription(str, float, str, str, str)
        +list_subscriptions()
        +update_subscription(int, str, float, str, str, str) bool
        +delete_subscription(int)
    }
    
    class analytics {
        +monthly_cost(Subscription) float
        +show_analytics()
    }
    
    storage ..> Subscription : Instantiates
    manager ..> Subscription : Uses
    analytics ..> Subscription : Uses
```

## Component Diagram

```mermaid
componentDiagram
    component "CLI Entry Point (main.py)" as CLI
    
    component "Business Logic" {
        component "Manager (CRUD)" as Mgr
        component "Analytics" as Ana
        component "Alerts" as Alrt
        component "Savings Analyzer" as Sav
        component "Search" as Srch
        component "CSV Export" as Exp
    }
    
    component "Core Services" {
        component "Validation & Date Math (utils.py)" as Util
        component "Data Models (models.py)" as Mod
    }
    
    component "Storage Layer (storage.py)" as Store
    
    database "subscriptions.json" as DB
    
    CLI --> Mgr
    CLI --> Ana
    CLI --> Alrt
    CLI --> Sav
    CLI --> Srch
    CLI --> Exp
    
    Mgr --> Store
    Ana --> Store
    Alrt --> Store
    Sav --> Store
    Srch --> Store
    Exp --> Store
    
    Store --> Util : auto-refreshes dates
    CLI --> Util : validates input
    
    Store --> DB
```

## Sequence Diagram: Data Load & Refresh Loop

```mermaid
sequenceDiagram
    participant CLI as Any Command (e.g. list)
    participant Store as storage.py
    participant Utils as utils.py
    participant Disk as subscriptions.json

    CLI->>Store: load_data()
    Store->>Disk: open(DATA_FILE)
    Disk-->>Store: JSON String
    Store->>Store: Parse to Subscription Objects
    Store->>Utils: refresh_renewal_dates(subs)
    
    loop For each sub
        alt date is in the past
            Utils->>Utils: advance_renewal_date()
        end
    end
    
    alt any dates were changed
        Utils-->>Store: return True
        Store->>Disk: save_data(subs)
    else no dates changed
        Utils-->>Store: return False
    end
    
    Store-->>CLI: Final list of Subscriptions
```
