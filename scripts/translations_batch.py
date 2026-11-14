# -*- coding: utf-8 -*-
"""Replace the 33 leaked English sentences with translations, in the page itself.

Not through the XPath dictionary - that is what broke. The sentences are literal
text in each page, so they are replaced literally, and a count proves each hit.
"""
import csv, os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'

DE = {
 'Plan your project with interactive voice • AI Engineer ready': 'Planen Sie Ihr Projekt per Sprachdialog • KI-Ingenieur bereit',
 'Distinct visual identities built with strategy, clarity, and consistency.': 'Unverwechselbare visuelle Identitäten – mit Strategie, Klarheit und Konsequenz.',
 'Modern, high-performance websites designed for clarity, trust, and growth.': 'Moderne, hochperformante Websites für Klarheit, Vertrauen und Wachstum.',
 'Hardened multi-region infrastructure on AWS and Azure with automated failover, zero-trust security, and 99.9% uptime SLA.': 'Gehärtete Multi-Region-Infrastruktur auf AWS und Azure mit automatischem Failover, Zero-Trust-Sicherheit und 99,9 % Verfügbarkeits-SLA.',
 'Complete digital and financial enterprise architecture fully customized for established corporations.': 'Vollständige digitale und finanzielle Unternehmensarchitektur, individuell zugeschnitten auf etablierte Konzerne.',
 'Custom-built enterprise ERP from scratch matching your exact workflows': 'Individuell entwickeltes Enterprise-ERP, exakt auf Ihre Abläufe zugeschnitten',
 'Distinct visual identities built with strategy, clarity, and consistency to anchor institutional trust.': 'Unverwechselbare visuelle Identitäten – strategisch, klar und konsequent, um institutionelles Vertrauen zu verankern.',
 'Modern, high-performance websites engineered for clarity, trust, and growth with instant loading.': 'Moderne, hochperformante Websites für Klarheit, Vertrauen und Wachstum – mit sofortiger Ladezeit.',
 'Intuitive online store architecture that turns casual visitors into repeat buyers with frictionless checkout.': 'Intuitive Shop-Architektur, die Besucher zu Stammkunden macht – mit reibungslosem Checkout.',
 'High-performance software library enabling developers and enterprises to integrate European tax compliance and cashflow forecasting into their applications.': 'Hochperformante Softwarebibliothek, mit der Entwickler und Unternehmen europäische Steuerkonformität und Liquiditätsprognosen in ihre Anwendungen integrieren.',
 'Military-grade AES-256 encryption engine protecting database backups and sensitive contracts, with automated zero-knowledge European cloud sync.': 'AES-256-Verschlüsselung nach Militärstandard für Datenbank-Backups und sensible Verträge, mit automatischer Zero-Knowledge-Cloud-Synchronisierung in Europa.',
 'Cloud ecosystem for any clinic, medical network, or telehealth center: video consultations, appointments, e-pharmacy, and patient/doctor portals with full GDPR compliance.': 'Cloud-Ökosystem für jede Praxis, jedes Ärztenetz und jedes Telemedizinzentrum: Videosprechstunden, Termine, E-Apotheke sowie Patienten- und Arztportale – DSGVO-konform.',
 'Have Proprietary Software or Systems You Want to License & Distribute Commercially?': 'Sie haben eigene Software oder Systeme und möchten sie kommerziell lizenzieren und vertreiben?',
 'Publish & Monetize Your Software': 'Veröffentlichen und monetarisieren Sie Ihre Software',
 'Connect directly with Lead Systems Architect Eng. Salim Aziza to review your system, define commercial licensing tiers, and publish it on our marketplace.': 'Sprechen Sie direkt mit dem leitenden Systemarchitekten Eng. Salim Aziza, um Ihr System zu prüfen, Lizenzstufen festzulegen und es in unserem Marktplatz zu veröffentlichen.',
 'Legally binding European regulatory certifications, enterprise SLA guarantees, and sovereign cloud infrastructure anchored in Amsterdam, the Netherlands.': 'Rechtsverbindliche europäische Zertifizierungen, Enterprise-SLA-Garantien und souveräne Cloud-Infrastruktur mit Standort Amsterdam.',
 'Rigorous alignment with ISO/IEC 27001 standards and SOC 2 Type II controls for enterprise risk governance.': 'Konsequente Ausrichtung an ISO/IEC 27001 und SOC 2 Type II für die unternehmerische Risikosteuerung.',
 'S&R CoreSync For Intelligent Solutions operates strictly under Dutch and European Union jurisdictions.': 'S&R CoreSync For Intelligent Solutions handelt ausschließlich nach niederländischem und EU-Recht.',
 'A genuine quantum leap in our multi-warehouse management and accounting workflows after deploying S&R CoreSync custom ERP. Exceptional precision and accountability.': 'Ein echter Quantensprung für unsere Lagerverwaltung und Buchhaltung nach der Einführung des individuellen ERP von S&R CoreSync. Außergewöhnliche Präzision und Nachvollziehbarkeit.',
 'Their dual mastery of cutting-edge software engineering and financial regulations saved us hundreds of manual hours every monthly close and revenue recognition cycle.': 'Ihre doppelte Kompetenz in modernster Softwareentwicklung und Finanzregulatorik spart uns bei jedem Monatsabschluss hunderte manuelle Stunden.',
 'The mobile platforms and executive cloud dashboards engineered by S&R CoreSync operate with blazing speed and bank-grade security. Our trusted technology partner.': 'Die mobilen Plattformen und Cloud-Dashboards von S&R CoreSync laufen mit höchster Geschwindigkeit und Sicherheit auf Bankniveau. Unser vertrauenswürdiger Technologiepartner.',
 'Discover How Much Your Organization Saves Annually with': 'Erfahren Sie, wie viel Ihre Organisation jährlich spart mit',
 'Calculate the exact financial savings and reclaimed administrative hours unlocked when automating your workflows and integrating your ERP with our architecture.': 'Berechnen Sie die genaue Ersparnis und die zurückgewonnenen Verwaltungsstunden durch automatisierte Abläufe und die Anbindung Ihres ERP an unsere Architektur.',
 'We engineer resilient cloud systems, high-performance web platforms, and automated ERP architectures driving enterprise growth across Europe and the Middle East.': 'Wir entwickeln robuste Cloud-Systeme, hochperformante Webplattformen und automatisierte ERP-Architekturen, die Unternehmenswachstum in Europa und im Nahen Osten vorantreiben.',
 'Receive monthly corporate ROI benchmarks, European cloud tax (BTW/VAT) automation updates, and exclusive enterprise sandbox access directly to your inbox.': 'Erhalten Sie monatlich ROI-Benchmarks, Updates zur europäischen Cloud-Steuerautomatisierung (BTW/USt.) und exklusiven Zugang zur Enterprise-Sandbox per E-Mail.',
 'Designed the full brand identity for Sarlor, an artisanal Syrian eatery in the Netherlands specializing in authentic Levantine pastries, manakish, and specialties.': 'Entwicklung der vollständigen Markenidentität für Sarlor, ein syrisches Handwerksrestaurant in den Niederlanden, spezialisiert auf levantinische Gebäcke, Manakish und Spezialitäten.',
 '"A disciplined visual system with sharp rhythm, memorable presence, and enduring resonance."': '„Ein diszipliniertes visuelles System mit klarem Rhythmus, einprägsamer Präsenz und dauerhafter Wirkung."',
 'Instant direct communication with the founding partners to discuss your requirements.': 'Sofortige direkte Kommunikation mit den Gründungspartnern, um Ihre Anforderungen zu besprechen.',
 'Cloud infrastructure with automated workflows, ledger sync, and inventory': 'Cloud-Infrastruktur mit automatisierten Abläufen, Kontensynchronisierung und Lagerverwaltung',
 'A concise walkthrough of our key enterprise modules before entering the complete sandbox.': 'Ein kurzer Überblick über unsere zentralen Unternehmensmodule vor dem Einstieg in die vollständige Sandbox.',
 'Access your central cloud management dashboard, deployments, and SLA tickets.': 'Zugriff auf Ihr zentrales Cloud-Dashboard, Ihre Deployments und SLA-Tickets.',
 '🛡️ Software License Management Portal • Exclusively for Salim Aziza, Founder & Chief Architect • S&R CoreSync For Intelligent Solutions': '🛡️ Portal für Software-Lizenzverwaltung • Exklusiv für Eng. Salim Aziza, Gründer und Chefarchitekt • S&R CoreSync For Intelligent Solutions',
 'Thank you for choosing S&R CoreSync For Intelligent Solutions. Your transaction is verified and registered under the Dutch fiscal framework.': 'Vielen Dank, dass Sie S&R CoreSync For Intelligent Solutions gewählt haben. Ihre Transaktion wurde geprüft und nach niederländischem Steuerrecht registriert.',
}

NL = {
 'Plan your project with interactive voice • AI Engineer ready': 'Plan uw project met spraak • AI-ingenieur gereed',
 'Distinct visual identities built with strategy, clarity, and consistency.': 'Onderscheidende visuele identiteiten, gebouwd met strategie, helderheid en consistentie.',
 'Modern, high-performance websites designed for clarity, trust, and growth.': 'Moderne, hoogwaardige websites voor helderheid, vertrouwen en groei.',
 'Hardened multi-region infrastructure on AWS and Azure with automated failover, zero-trust security, and 99.9% uptime SLA.': 'Beveiligde multi-region infrastructuur op AWS en Azure met automatische failover, zero-trust beveiliging en 99,9% uptime-SLA.',
 'Complete digital and financial enterprise architecture fully customized for established corporations.': 'Complete digitale en financiële bedrijfsarchitectuur, volledig op maat voor gevestigde ondernemingen.',
 'Custom-built enterprise ERP from scratch matching your exact workflows': 'Maatwerk ERP voor ondernemingen, vanaf nul gebouwd op uw processen',
 'Distinct visual identities built with strategy, clarity, and consistency to anchor institutional trust.': 'Onderscheidende visuele identiteiten met strategie, helderheid en consistentie om institutioneel vertrouwen te verankeren.',
 'Modern, high-performance websites engineered for clarity, trust, and growth with instant loading.': 'Moderne, hoogwaardige websites voor helderheid, vertrouwen en groei, met directe laadtijd.',
 'Intuitive online store architecture that turns casual visitors into repeat buyers with frictionless checkout.': 'Intuïtieve webwinkelarchitectuur die bezoekers omzet in terugkerende kopers, met een soepele afrekenflow.',
 'High-performance software library enabling developers and enterprises to integrate European tax compliance and cashflow forecasting into their applications.': 'Hoogwaardige softwarebibliotheek waarmee ontwikkelaars en bedrijven Europese belastingnaleving en cashflowprognoses in hun applicaties integreren.',
 'Military-grade AES-256 encryption engine protecting database backups and sensitive contracts, with automated zero-knowledge European cloud sync.': 'AES-256-encryptie op militaire sterkte voor databaseback-ups en gevoelige contracten, met automatische zero-knowledge cloud-synchronisatie in Europa.',
 'Cloud ecosystem for any clinic, medical network, or telehealth center: video consultations, appointments, e-pharmacy, and patient/doctor portals with full GDPR compliance.': 'Cloud-ecosysteem voor elke kliniek, elk medisch netwerk of telehealthcentrum: videoconsulten, afspraken, e-apotheek en patiënt- en artsenportalen, volledig AVG-conform.',
 'Have Proprietary Software or Systems You Want to License & Distribute Commercially?': 'Hebt u eigen software of systemen die u commercieel wilt licenseren en distribueren?',
 'Publish & Monetize Your Software': 'Publiceer en monetiseer uw software',
 'Connect directly with Lead Systems Architect Eng. Salim Aziza to review your system, define commercial licensing tiers, and publish it on our marketplace.': 'Spreek direct met lead system architect Eng. Salim Aziza om uw systeem te beoordelen, licentieniveaus vast te leggen en het in onze marktplaats te publiceren.',
 'Legally binding European regulatory certifications, enterprise SLA guarantees, and sovereign cloud infrastructure anchored in Amsterdam, the Netherlands.': 'Juridisch bindende Europese certificeringen, enterprise SLA-garanties en soevereine cloudinfrastructuur in Amsterdam.',
 'Rigorous alignment with ISO/IEC 27001 standards and SOC 2 Type II controls for enterprise risk governance.': 'Strikte aansluiting op ISO/IEC 27001 en SOC 2 Type II voor governanceto ezicht op ondernemingsrisico.',
 'S&R CoreSync For Intelligent Solutions operates strictly under Dutch and European Union jurisdictions.': 'S&R CoreSync For Intelligent Solutions werkt uitsluitend onder Nederlands en EU-recht.',
 'A genuine quantum leap in our multi-warehouse management and accounting workflows after deploying S&R CoreSync custom ERP. Exceptional precision and accountability.': 'Een echte sprong voorwaarts in ons multi-magazijnbeheer en onze boekhouding na de invoering van het maatwerk-ERP van S&R CoreSync. Uitzonderlijke precisie en verantwoording.',
 'Their dual mastery of cutting-edge software engineering and financial regulations saved us hundreds of manual hours every monthly close and revenue recognition cycle.': 'Hun dubbele expertise in geavanceerde softwareontwikkeling en financiële regelgeving bespaart ons maandelijks honderden handmatige uren.',
 'The mobile platforms and executive cloud dashboards engineered by S&R CoreSync operate with blazing speed and bank-grade security. Our trusted technology partner.': 'De mobiele platforms en clouddashboards van S&R CoreSync werken razendsnel en met beveiliging op bankniveau. Onze vertrouwde technologiepartner.',
 'Discover How Much Your Organization Saves Annually with': 'Ontdek hoeveel uw organisatie jaarlijks bespaart met',
 'Calculate the exact financial savings and reclaimed administrative hours unlocked when automating your workflows and integrating your ERP with our architecture.': 'Bereken de exacte financiële besparing en de teruggewonnen administratieve uren door automatisering en koppeling van uw ERP aan onze architectuur.',
 'We engineer resilient cloud systems, high-performance web platforms, and automated ERP architectures driving enterprise growth across Europe and the Middle East.': 'Wij bouwen veerkrachtige cloudsystemen, hoogwaardige webplatforms en geautomatiseerde ERP-architecturen die groei stimuleren in Europa en het Midden-Oosten.',
 'Receive monthly corporate ROI benchmarks, European cloud tax (BTW/VAT) automation updates, and exclusive enterprise sandbox access directly to your inbox.': 'Ontvang maandelijks ROI-benchmarks, updates over Europese cloudbelasting (btw/vat) en exclusieve toegang tot de enterprise-sandbox in uw inbox.',
 'Designed the full brand identity for Sarlor, an artisanal Syrian eatery in the Netherlands specializing in authentic Levantine pastries, manakish, and specialties.': 'De volledige merkidentiteit ontworpen voor Sarlor, een Syrisch ambachtelijk restaurant in Nederland, gespecialiseerd in authentiek Levantijns gebak, manakish en specialiteiten.',
 '"A disciplined visual system with sharp rhythm, memorable presence, and enduring resonance."': '“Een gedisciplineerd visueel systeem met scherp ritme, blijvende présence en duurzame weerklank.”',
 'Instant direct communication with the founding partners to discuss your requirements.': 'Directe communicatie met de oprichtende partners om uw wensen te bespreken.',
 'Cloud infrastructure with automated workflows, ledger sync, and inventory': 'Cloudinfrastructuur met geautomatiseerde processen, grootboeksynchronisatie en voorraadbeheer',
 'A concise walkthrough of our key enterprise modules before entering the complete sandbox.': 'Een korte rondleiding langs onze belangrijkste enterprise-modules voordat u de volledige sandbox betreedt.',
 'Access your central cloud management dashboard, deployments, and SLA tickets.': 'Toegang tot uw centrale clouddashboard, deployments en SLA-tickets.',
 '🛡️ Software License Management Portal • Exclusively for Salim Aziza, Founder & Chief Architect • S&R CoreSync For Intelligent Solutions': '🛡️ Portaal voor softwarelicentiebeheer • Exclusief voor Eng. Salim Aziza, oprichter en chief architect • S&R CoreSync For Intelligent Solutions',
 'Thank you for choosing S&R CoreSync For Intelligent Solutions. Your transaction is verified and registered under the Dutch fiscal framework.': 'Dank u voor het kiezen van S&R CoreSync For Intelligent Solutions. Uw transactie is geverifieerd en geregistreerd volgens het Nederlandse fiscale kader.',
}

print('de entries:', len(DE), '· nl entries:', len(NL))
