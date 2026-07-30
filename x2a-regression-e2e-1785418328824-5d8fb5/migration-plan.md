# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a standardized Ansible structure and migrating Chef InSpec tests to Ansible-compatible testing frameworks. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used in the website deployment. Can be directly used in Ansible.

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on setup-automate scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Convert InSpec tests to Ansible assert modules or custom modules

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure:
  - Molecule provides similar functionality for testing Ansible roles and playbooks
  - Supports multiple drivers (Vagrant, Docker, etc.) similar to Test Kitchen

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Ansible AWX/Tower for web UI and API
  - Ansible Galaxy for role sharing
  - Ansible Collections for organizing content

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Migration should maintain or improve security posture:
  - Ensure TLS 1.2+ is enforced (already implemented in poodle_fix.yml)
  - Consider adding modern cipher suite configurations
  - Implement automatic certificate renewal if moving to production

- **SSH Hardening**: The SSH InSpec profile checks for secure SSH configuration:
  - Implement equivalent checks using Ansible's assert module or Molecule/Testinfra
  - Consider adding an Ansible role for SSH hardening based on the existing tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely or replaced with Let's Encrypt integration

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks:
  - InSpec has a more declarative syntax for compliance testing
  - Solution: Use Ansible assert modules with custom modules where needed, or integrate with Testinfra

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting:
  - Chef Automate provides compliance reporting that needs equivalent in Ansible
  - Solution: Integrate with AWX/Tower reporting or third-party compliance tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need structural reorganization
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires conversion to Ansible testing framework
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires complete replacement with Ansible roles

### Assumptions

1. The repository is primarily used for demonstration/examples rather than production workloads (based on README content)
2. The InSpec tests are used for validation of infrastructure rather than continuous compliance monitoring
3. The deployment scripts are for setting up test environments rather than production Chef infrastructure
4. No external data sources or complex variable structures are in use
5. No existing Ansible inventory or group_vars/host_vars are present
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions

## Detailed Migration Steps

### 1. Restructure Ansible Content

Create a standard Ansible project structure:

```
ansible/
├── inventory/
│   └── hosts.yml
├── group_vars/
│   └── all.yml
├── roles/
│   ├── apache_https/
│   │   ├── tasks/
│   │   ├── templates/
│   │   ├── handlers/
│   │   └── defaults/
│   └── ssl_hardening/
│       ├── tasks/
│       └── handlers/
├── playbooks/
│   ├── website_https.yml
│   └── poodle_fix.yml
└── tests/
    └── molecule/
```

### 2. Convert InSpec Tests

Create equivalent tests using Ansible Molecule:

```yaml
# Example verification.yml for Molecule
- name: Verify
  hosts: all
  tasks:
    - name: Check if port 443 is listening
      wait_for:
        port: 443
        timeout: 10
      register: port_check
      failed_when: not port_check.started

    - name: Check website content
      uri:
        url: https://localhost/
        return_content: yes
        validate_certs: no
      register: webpage
      failed_when: "'Hello, world!' not in webpage.content"
      
    - name: Check SSL protocols
      shell: "nmap --script ssl-enum-ciphers -p 443 localhost"
      register: ssl_check
      changed_when: false
      failed_when: 
        - "'SSLv3' in ssl_check.stdout"
        - "'TLSv1.2' not in ssl_check.stdout"
```

### 3. Replace Chef Deployment Scripts

Create Ansible roles for deployment:

```yaml
# Example playbook for deploying Ansible AWX
- name: Deploy Ansible AWX
  hosts: automation_servers
  become: yes
  roles:
    - role: ansible_automation_platform
      vars:
        admin_user: "{{ vault_admin_user }}"
        admin_password: "{{ vault_admin_password }}"
        organization_name: "{{ organization }}"
```

### 4. Documentation and Knowledge Transfer

- Create README files for each role explaining its purpose and usage
- Document testing procedures using Molecule
- Provide examples of inventory structure and variable management