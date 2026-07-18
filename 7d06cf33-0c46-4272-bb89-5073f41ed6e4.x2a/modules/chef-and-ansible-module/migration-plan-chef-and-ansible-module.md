---
source-path: chef-and-ansible
---

# Analysis: chef-and-ansible

**TLDR**: This repository demonstrates using Chef InSpec for compliance testing with Ansible deployments. It contains Ansible playbooks that set up an Apache web server with HTTPS and SSL security configurations, along with InSpec tests to verify compliance.

## Repository Structure

This repository contains:

1. **Ansible Playbooks**:
   - `website_https.yml`: Sets up an Apache web server with HTTPS using a self-signed certificate
   - `poodle_fix.yml`: Addresses the POODLE vulnerability by restricting SSL protocols to TLSv1.2

2. **Chef InSpec Tests**:
   - `tests/website_https_verify.rb`: Verifies HTTPS configuration and security
   - `tests/ssh_profile.rb`: Checks SSH configuration for compliance with security standards

3. **Supporting Files**:
   - `README.md`: Explains the purpose of the repository
   - `index.html`: Sample HTML content
   - `kitchen.yml`: Likely for Test Kitchen configuration (content not examined)

## Ansible Playbook Details

### website_https.yml

This playbook configures an Apache web server with HTTPS:

1. **Package Installation**:
   - Installs Apache 2.4.41
   - Installs supporting packages: curl, openssl, python3-openssl

2. **SSL Certificate Generation**:
   - Creates a directory for certificates
   - Generates a private key, CSR, and self-signed certificate

3. **Web Server Configuration**:
   - Creates a virtual host configuration for HTTPS
   - Sets up a "Hello World" website
   - Disables the default site and enables the new one
   - Activates SSL module in Apache

4. **Service Management**:
   - Restarts Apache and SSH services when configuration changes

### poodle_fix.yml

This playbook addresses the POODLE vulnerability:

1. **Security Configuration**:
   - Modifies Apache's SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2 for secure connections

2. **Service Management**:
   - Restarts Apache and SSH services after configuration changes

## InSpec Tests

### website_https_verify.rb

Tests the HTTPS configuration:
- Verifies port 443 is listening
- Checks that the website returns a 200 status code
- Confirms the page contains "Hello, world!"
- Ensures SSL3 is disabled (POODLE vulnerability mitigation)
- Verifies TLS 1.2 is enabled

### ssh_profile.rb

Tests SSH security configuration:
- Verifies that root login via SSH is disabled
- Includes detailed rationale and compliance information
- References security standards (SRG-OS-000112, V-38607, etc.)

## Conclusion

This repository demonstrates how to use Chef InSpec for compliance testing alongside Ansible deployments. The Ansible playbooks set up a secure web server, and the InSpec tests verify that the configuration meets security requirements.

Since this is already an Ansible implementation (not a Chef cookbook requiring migration), no migration plan is needed. The repository shows how Chef's compliance tools (InSpec) can be used with Ansible for a hybrid approach to infrastructure automation and compliance.