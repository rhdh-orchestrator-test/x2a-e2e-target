---
source-path: chef-and-ansible/website_https.yml
---

Now I'll analyze the content and create a migration plan for this Ansible role:

# Migration Plan: ansible-https-website

**TLDR**: This role sets up an Apache web server with HTTPS support using a self-signed certificate. It needs modernization to use FQCN module names, proper boolean syntax, quoted file modes, and improved command module usage with proper change detection.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server and SSL dependencies (curl, openssl, python3-openssl)
- Creates SSL certificates directory and generates self-signed certificates
- Configures a virtual host for HTTPS
- Creates a simple "Hello World" website
- Enables SSL module and the custom virtual host
- Disables the default virtual host
- Restarts Apache service when configuration changes

## File Structure

**IMPORTANT: The role is currently a standalone playbook, not a proper Ansible role structure.**

```
website_https.yml
```

## Module Explanation

The role performs operations in this order:

1. **website_https.yml** (`chef-and-ansible/website_https.yml`):
   - Updates apt cache and installs Apache and SSL dependencies
   - Creates certificate directory and generates self-signed SSL certificates
   - Configures a virtual host for HTTPS and deploys a simple website
   - Enables SSL module and the custom virtual host, disables default site
   - Restarts Apache when configuration changes
   - Ansible module mapping: Multiple legacy modules → modern FQCN equivalents

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN |
| `update_cache=true` | `update_cache: true` | website_https.yml | Boolean syntax |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted file mode |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted file mode |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted file mode |
| `command: a2dissite` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Idempotency |
| `command: a2ensite` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Idempotency |
| `command: a2enmod` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Idempotency |
| Playbook structure | Role structure | website_https.yml | Convert to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No .j2 templates are used in this playbook. The configuration is stored in variables and deployed using the copy module.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `conftext`: string, default is the Apache virtual host configuration, description: "Apache virtual host configuration for HTTPS"
- `webtext`: string, default is the HTML content, description: "HTML content for the Hello World website"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None (using variables instead of templates)

## Pre-flight checks:
```bash
# Verify Apache is installed and running
systemctl status apache2

# Verify SSL module is enabled
apache2ctl -M | grep ssl

# Verify virtual host configuration
apache2ctl -S

# Verify SSL certificate
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Test HTTPS connection
curl -k https://localhost/
```

## Migration Steps

1. **Create proper role structure**:
   ```
   ansible-https-website/
   ├── defaults/
   │   └── main.yml
   ├── handlers/
   │   └── main.yml
   ├── meta/
   │   ├── main.yml
   │   └── argument_specs.yml
   ├── tasks/
   │   └── main.yml
   └── README.md
   ```

2. **Extract variables to defaults/main.yml**:
   ```yaml
   ---
   # Apache virtual host configuration for HTTPS
   conftext: |
     <VirtualHost *:443>
      DocumentRoot "/var/www/helloworld"
      SSLEngine on
      SSLCertificateFile /etc/apache2/certs/apache.crt
      SSLCertificateKeyFile /etc/apache2/certs/apache.key
       <Directory "/var/www/helloworld">
         allow from all
         Options None
         Require all granted
       </Directory>
     </VirtualHost>
   
   # HTML content for the Hello World website
   webtext: |
    <html>
      <head><title>Test Site</title>/head>
      <body>
       <h1>Hello, world!</h1>
       <p>The site is up and running</p>
      </body>
    </html>
   ```

3. **Extract handlers to handlers/main.yml**:
   ```yaml
   ---
   - name: Restart sshd
     ansible.builtin.service:
       name: sshd
       state: restarted
       
   - name: Restart apache
     ansible.builtin.service:
       name: apache2
       state: restarted
   ```

4. **Extract tasks to tasks/main.yml with modernization**:
   ```yaml
   ---
   - name: Update apt cache 
     ansible.builtin.apt:
       update_cache: true
   
   - name: Install necessary packages 
     ansible.builtin.apt: 
       name: apache2=2.4.41-4ubuntu3.10
   
   - name: Install curl, openssl, PyOpenSSL
     ansible.builtin.apt:
       pkg:
       - curl
       - openssl
       - python3-openssl
   
   - name: Create a directory for certs
     ansible.builtin.file: 
       path: /etc/apache2/certs
       state: directory
       mode: '0640'
   
   - name: Generate an openssl key
     community.crypto.openssl_privatekey:
       path: /etc/apache2/certs/apache.key
   
   - name: Generate an openssl csr
     community.crypto.openssl_csr:
       path: /etc/apache2/certs/apache.csr
       privatekey_path: /etc/apache2/certs/apache.key
       common_name: myhost
   
   - name: Generate a self-signed openssl certificate
     community.crypto.openssl_certificate:
       path: /etc/apache2/certs/apache.crt
       privatekey_path: /etc/apache2/certs/apache.key
       csr_path: /etc/apache2/certs/apache.csr
       provider: selfsigned
       
   - name: Configure Hello World virtual host 
     ansible.builtin.copy: 
       content: "{{ conftext }}"
       dest: /etc/apache2/sites-available/helloworld.conf
       mode: '0640'
       force: true
   
   - name: Create the helloworld directory 
     ansible.builtin.file: 
       path: /var/www/helloworld 
       state: directory 
       mode: '0755'
       
   - name: Deploy the Hello World website 
     ansible.builtin.copy: 
       content: "{{ webtext }}"
       dest: /var/www/helloworld/index.html
       owner: root
       group: root
       mode: '0644'
       force: true
   
   - name: Deactivate the default virtualhost 
     ansible.builtin.command: a2dissite 000-default
     register: disable_default
     changed_when: "'Site 000-default disabled' in disable_default.stdout"
     
   - name: Activate the virtualhost 
     ansible.builtin.command: a2ensite helloworld
     register: enable_site
     changed_when: "'Enabling site helloworld' in enable_site.stdout"
     notify:
       - Restart apache
   
   - name: Activate SSL on Apache
     ansible.builtin.command: a2enmod ssl
     register: enable_ssl
     changed_when: "'Enabling module ssl' in enable_ssl.stdout"
     notify:
       - Restart sshd
       - Restart apache
   ```

5. **Create meta/main.yml**:
   ```yaml
   ---
   galaxy_info:
     role_name: https_website
     author: your_name
     description: Sets up an Apache web server with HTTPS support
     license: MIT
     min_ansible_version: 2.9
     platforms:
       - name: Ubuntu
         versions:
           - focal
     galaxy_tags:
       - web
       - apache
       - https
       - ssl
   
   dependencies: []
   ```

6. **Create meta/argument_specs.yml**:
   ```yaml
   ---
   argument_specs:
     main:
       short_description: Sets up an Apache web server with HTTPS support
       description:
         - This role installs and configures Apache with SSL support
         - Creates a self-signed certificate
         - Deploys a simple Hello World website
       options:
         conftext:
           type: str
           description: Apache virtual host configuration for HTTPS
           required: false
         webtext:
           type: str
           description: HTML content for the Hello World website
           required: false
   ```

7. **Create collections/requirements.yml**:
   ```yaml
   ---
   collections:
     - name: community.crypto
       version: ">=2.0.0"
   ```