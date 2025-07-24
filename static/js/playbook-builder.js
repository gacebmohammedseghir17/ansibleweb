// Playbook Builder JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize component checkboxes
    initializeComponentCheckboxes();
    
    // Initialize the playbook content editor
    initializePlaybookEditor();
});

function initializeComponentCheckboxes() {
    // Handle Roles checkbox
    const includeRolesCheckbox = document.getElementById('includeRoles');
    if (includeRolesCheckbox) {
        includeRolesCheckbox.addEventListener('change', function() {
            const rolesSection = document.getElementById('rolesSection');
            rolesSection.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // Handle Templates checkbox
    const includeTemplatesCheckbox = document.getElementById('includeTemplates');
    if (includeTemplatesCheckbox) {
        includeTemplatesCheckbox.addEventListener('change', function() {
            const templatesSection = document.getElementById('templatesSection');
            templatesSection.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // Handle Variables checkbox
    const includeVarsCheckbox = document.getElementById('includeVars');
    if (includeVarsCheckbox) {
        includeVarsCheckbox.addEventListener('change', function() {
            const varsSection = document.getElementById('varsSection');
            varsSection.style.display = this.checked ? 'block' : 'none';
        });
    }
}

function initializePlaybookEditor() {
    const playbookContent = document.getElementById('playbookContent');
    if (playbookContent) {
        // Auto-update preview as user types
        playbookContent.addEventListener('input', function() {
            updatePlaybookPreview();
        });
    }
}

function updatePlaybookPreview() {
    // This function can be expanded to validate YAML and provide syntax highlighting
    const content = document.getElementById('playbookContent').value;
    // Future enhancement: Add YAML validation here
}

// Functions for adding components
function addRole() {
    const roleName = document.getElementById('roleName').value.trim();
    const roleContent = document.getElementById('roleContent').value.trim();
    
    if (!roleName) {
        showToast('Please enter a role name', 'error');
        return;
    }
    
    const rolesList = document.getElementById('rolesList');
    const roleItem = document.createElement('div');
    roleItem.className = 'list-group-item d-flex justify-content-between align-items-center';
    roleItem.innerHTML = `
        <div>
            <strong>${roleName}</strong>
            <p class="mb-0 text-muted small">${roleContent ? 'Custom role content defined' : 'Default role structure'}</p>
        </div>
        <button class="btn btn-sm btn-outline-danger" onclick="this.parentNode.remove()">Remove</button>
    `;
    
    rolesList.appendChild(roleItem);
    
    // Clear inputs
    document.getElementById('roleName').value = '';
    document.getElementById('roleContent').value = '';
    
    // Update playbook content
    updatePlaybookWithComponents();
}

function addTemplate() {
    const templateName = document.getElementById('templateName').value.trim();
    const templateContent = document.getElementById('templateContent').value.trim();
    
    if (!templateName) {
        showToast('Please enter a template name', 'error');
        return;
    }
    
    const templatesList = document.getElementById('templatesList');
    const templateItem = document.createElement('div');
    templateItem.className = 'list-group-item d-flex justify-content-between align-items-center';
    templateItem.innerHTML = `
        <div>
            <strong>${templateName}</strong>
            <p class="mb-0 text-muted small">${templateContent ? 'Custom template content defined' : 'Empty template'}</p>
        </div>
        <button class="btn btn-sm btn-outline-danger" onclick="this.parentNode.remove()">Remove</button>
    `;
    
    templatesList.appendChild(templateItem);
    
    // Clear inputs
    document.getElementById('templateName').value = '';
    document.getElementById('templateContent').value = '';
    
    // Update playbook content
    updatePlaybookWithComponents();
}

function addVariable() {
    const varName = document.getElementById('varName').value.trim();
    const varValue = document.getElementById('varValue').value.trim();
    
    if (!varName) {
        showToast('Please enter a variable name', 'error');
        return;
    }
    
    const variablesList = document.getElementById('variablesList');
    const varItem = document.createElement('div');
    varItem.className = 'list-group-item d-flex justify-content-between align-items-center';
    varItem.innerHTML = `
        <div>
            <strong>${varName}: </strong>
            <span>${varValue}</span>
        </div>
        <button class="btn btn-sm btn-outline-danger" onclick="this.parentNode.remove()">Remove</button>
    `;
    
    variablesList.appendChild(varItem);
    
    // Clear inputs
    document.getElementById('varName').value = '';
    document.getElementById('varValue').value = '';
    
    // Update playbook content
    updatePlaybookWithComponents();
}

function updatePlaybookWithComponents() {
    // This function will update the playbook content based on selected components
    // For now, we'll just add a placeholder implementation
    const playbookContent = document.getElementById('playbookContent');
    if (!playbookContent) return;
    
    // Get the current content
    let content = playbookContent.value;
    
    // If it's empty or just has the default content, start with a basic structure
    if (!content || content.trim() === '---\n# Your playbook content here') {
        content = `---\n- name: ${document.getElementById('playbookName').value || 'My Playbook'}\n  hosts: ${document.getElementById('playbookInventory').value || 'all'}\n`;
        
        // Add vars section if there are variables
        if (document.getElementById('includeVars').checked && document.getElementById('variablesList').children.length > 0) {
            content += '  vars:\n';
            // We would add actual variables here in a real implementation
            content += '    # Variables will be added here\n';
        }
        
        content += '  tasks:\n    # Tasks will be added here\n';
    }
    
    playbookContent.value = content;
}