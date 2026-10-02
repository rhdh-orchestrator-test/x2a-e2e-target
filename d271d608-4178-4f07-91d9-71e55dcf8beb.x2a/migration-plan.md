# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance tests and Ansible playbooks demonstrating integration between Chef InSpec and Ansible for compliance automation. The migration scope is limited as this is primarily a demonstration repository with existing Ansible playbooks and Chef InSpec tests that showcase compliance validation workflows.

**Migration Complexity**: Low to Medium
**Estimated Timeline**: 1-2 weeks
**Primary Challenge**: Converting Chef InSpec compliance tests to native Ansible compliance modules or alternative testing frameworks

## Module Migration Plan

This repository contains Chef InSpec compliance tests and supporting Ansible automation that need migration planning:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificate generation, and virtual host management for a test website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL, Apache virtual host configuration, security hardening with TLS 1.2

**ssl-security-hardening**:
- Description: SSL/TLS security configuration fix to disable vulnerable protocols and enforce TLS 1.2 (POODLE vulnerability mitigation)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, vulnerability remediation, service restart handling

**compliance-validation-suite**:
- Description: Chef InSpec compliance tests for HTTPS functionality, SSL protocol validation, and SSH security configuration
- Path: chef-and-ansible/tests/
- Technology: Chef InSpec
- Key Features: Port listening verification, HTTPS response validation, SSL protocol compliance checks, SSH root login security controls

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification - needs conversion to molecule or native Ansible testing
- `deploy-automate.sh`: Chef Automate and Infra Server deployment script - can be retired as part of Chef infrastructure decommissioning
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script - can be retired as part of Chef infrastructure decommissioning
- `index.html`: Static demonstration web page - no migration needed

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (based on kitchen.yml platform specification and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible compliance modules (ansible.posix.firewalld, community.crypto.openssl_certificate_info) or Testinfra for Python-based testing
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and validation
- **Chef Automate/Server**: Decommission Chef infrastructure components as they are only used for demonstration purposes

### Security Considerations
- **SSL/TLS Configuration**: The existing Ansible playbooks already implement proper SSL security practices:
  - Self-signed certificate generation with proper key management
  - TLS 1.2 enforcement and SSL 3.0 disabling (POODLE fix)
  - Proper file permissions on certificate files (0640)
- **SSH Security**: InSpec tests validate SSH root login restrictions - migrate to Ansible assert tasks or dedicated security scanning tools
- **Credential Management**: Current implementation uses hardcoded values in deployment scripts - should implement Ansible Vault for sensitive data in production environments

### Technical Challenges
- **InSpec Test Conversion**: Converting Chef InSpec compliance tests to equivalent Ansible validation tasks or alternative testing frameworks
  - Challenge: InSpec's rich compliance testing DSL needs mapping to Ansible assert modules or external tools
  - Mitigation: Use ansible.builtin.assert, ansible.builtin.uri, and community.crypto modules for equivalent validation
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule for integrated testing
  - Challenge: Different testing paradigms and configuration syntax
  - Mitigation: Leverage existing Ansible playbooks and convert InSpec tests to Testinfra or native Ansible assertions
- **Compliance Reporting**: Loss of InSpec's compliance reporting capabilities
  - Challenge: InSpec provides structured compliance reports with STIG/CIS mappings
  - Mitigation: Implement custom reporting with Ansible facts or integrate with external compliance tools

### Migration Order
1. **SSL Security Hardening** (already complete - existing Ansible playbook)
2. **Apache HTTPS Website** (already complete - existing Ansible playbook) 
3. **Compliance Test Conversion** (convert InSpec tests to Ansible assertions or Testinfra)
4. **Testing Framework Migration** (replace Test Kitchen with Molecule)
5. **Infrastructure Cleanup** (decommission Chef Automate deployment scripts)

### Assumptions
- The target environment will continue to use Ubuntu/Debian-based systems as indicated by apt package manager usage
- Vagrant-based local testing environment will be maintained or replaced with equivalent containerized testing
- The demonstration nature of this repository means production-grade secret management is not currently implemented
- InSpec compliance tests represent the minimum required security validation that must be preserved in the migrated solution
- The existing Ansible playbooks are considered the target state, with InSpec tests providing validation requirements
- No external Chef cookbook dependencies exist since this is a standalone demonstration repository
- The Chef Automate/Server deployment scripts are for demonstration purposes only and not part of production infrastructure