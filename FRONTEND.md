# Portal Frontend Architecture

This document briefly explains the frontend stack and architectural decisions for the administrative portal in the Haulage Truck Management System.

## Stack Overview
- **Framework**: Django Server-Side Rendering (Templates)
- **CSS Framework**: Bootstrap 5 (via CDN)
- **Javascript**: None/Minimal (only Bootstrap's bundled JS for simple interactions like dismissible alerts)
- **Authentication**: Native Django Session Auth (`User` model)

## Design Philosophy: "Backend Engineer First"
The UI was intentionally designed to be purely functional, minimalistic, and straightforward, avoiding heavy modern JavaScript frameworks (like React or Vue) or complex styling abstractions. 
- It uses basic HTML tables, standard Bootstrap forms, and simple cards. 
- It serves as an immediate, practical interface for managing the backend database.
- Focus is entirely placed on robust business logic (handling truck maintenance availability, routing concurrent jobs, etc.) rather than unnecessary visual flair.

## Mobile Handling
Instead of full responsive fluid grids adjusting to every breakpoint, the portal is strictly a desktop/tablet-class web application:
- Unauthenticated screens (like the Login page) remain responsive.
- However, if an authenticated administrator logs in on a small mobile device, they are greeted with a warning indicating the interface requires a wider screen. The main data tables and routing assignments require space, removing the need for deeply complex mobile collapsing menus.

## App Structure
The frontend lives entirely within the Django `portal` app, neatly quarantined from the core API and data models.

* **Views** (`portal/views.py`): Contains basic function-based views to handle CRUD interactions, relying entirely on the Django ORM to aggregate data (e.g. `has_active_job` subqueries) before sending it to the view.
* **Forms** (`portal/forms.py`): Minimal `ModelForm` usage that passes the `form-control` Bootstrap class directly to rendered inputs.
* **Templates** (`portal/templates/portal/`): Contains the base layout, dashboard, and sub-folders for Jobs, Trucks, and Drivers. All templates inherit from `base.html`.
