const deleteModal = document.getElementById('deleteModal')
if (deleteModal) {
  deleteModal.addEventListener('show.bs.modal', event => {
    // Button that triggered the modal
    const button = event.relatedTarget
    // Extract info from data-bs-* attributes
    const identifier = button.getAttribute('data-bs-item')
    const itemId = button.getAttribute('data-bs-item-id')
    const itemType = button.getAttribute('data-bs-item-type')
    // Update the hidden inputs
    const hiddenId = deleteModal.querySelector('#delete-id')
    const hiddenType = deleteModal.querySelector('#delete-type')
    hiddenId.value = itemId
    hiddenType.value = itemType
    // Update the modal's content.
    const modalTitle = deleteModal.querySelector('.modal-title')
    const modalBodyItem = deleteModal.querySelector('.modal-body p#delete-item')
    const modalBodyItemType = deleteModal.querySelector('.modal-body p#delete-item-type')
    const modalBodyItemId = deleteModal.querySelector('.modal-body p#delete-item-id')
    modalTitle.textContent = `Are you sure you want to delete this item?`
    modalBodyItem.innerHTML = identifier
    modalBodyItemType.innerHTML = "Type: " + itemType
    modalBodyItemId.innerHTML = "Id: " + itemId
  })
}

const deleteFileVectorModal = document.getElementById('deleteFileVectorModal')
if (deleteFileVectorModal) {
  deleteFileVectorModal.addEventListener('show.bs.modal', event => {
    // Button that triggered the modal
    const button = event.relatedTarget
    // Extract info from data-bs-* attributes
    const itemSource = button.getAttribute('data-bs-item-source')
    const itemFileId = button.getAttribute('data-bs-item-file-id')
    // Update the hidden inputs
    const hiddenSource = deleteFileVectorModal.querySelector('#delete-source')
    const hiddenFileId = deleteFileVectorModal.querySelector('#delete-file-id')
    hiddenSource.value = itemSource
    hiddenFileId.value = itemFileId
    // Update the modal's content.
    const modalTitle = deleteFileVectorModal.querySelector('.modal-title')
    const modalBodyItemFileSource = deleteFileVectorModal.querySelector('.modal-body p#delete-item-file-source')
    modalTitle.textContent = `Are you sure you want to delete all chunks of this item? Only the chunks in the vector database will be deleted the uploaded file will remain.`
    modalBodyItemFileSource.innerHTML = "Source Id: " + itemSource
  })
}

const deleteVectorModal = document.getElementById('deleteVectorModal')
if (deleteVectorModal) {
  deleteVectorModal.addEventListener('show.bs.modal', event => {
    // Button that triggered the modal
    const button = event.relatedTarget
    // Extract info from data-bs-* attributes
    const identifier = button.getAttribute('data-bs-item')
    const editPath = button.getAttribute('data-bs-edit-path')
    const itemId = button.getAttribute('data-bs-item-id')
    const itemFileId = button.getAttribute('data-bs-item-entity-id')
    // Update the hidden inputs
    const hiddenId = deleteVectorModal.querySelector('#delete-id')
    const hiddenEditPath = deleteVectorModal.querySelector('#delete-edit-path')
    const hiddenFileId = deleteVectorModal.querySelector('#delete-entity-id')
    hiddenId.value = itemId
    hiddenEditPath.value = editPath
    hiddenFileId.value = itemFileId
    // Update the modal's content.
    const modalTitle = deleteVectorModal.querySelector('.modal-title')
    const modalBodyItem = deleteVectorModal.querySelector('.modal-body p#delete-item')
    const modalBodyItemId = deleteVectorModal.querySelector('.modal-body p#delete-item-id')
    modalTitle.textContent = `Are you sure you want to delete this item?`
    modalBodyItem.innerHTML = identifier
    modalBodyItemId.innerHTML = "Vector Id: " + itemId
  })
}

const deleteModel = document.getElementById('deleteModel')
if (deleteModel) {
  deleteModel.addEventListener('show.bs.modal', event => {
    // Button that triggered the modal
    const button = event.relatedTarget
    // Extract info from data-bs-* attributes
    const identifier = button.getAttribute('data-bs-item')
    console.log(identifier)
    // Update the hidden inputs
    const hiddenItem = deleteModel.querySelector('#delete-item')
    hiddenItem.value = identifier
    // Update the modal's content.

    const modalTitle = deleteModel.querySelector('.modal-title')
    modalTitle.textContent = `Delete Ollama Model`
    const modalBodyInfo = deleteModel.querySelector('.modal-body #delete-model')
    modalBodyInfo.innerHTML = `Are you sure you want to delete this item? You are deleting the installed ollama model from the ollama repository. If you are using this in another application you will have to install it again to use it there. I can not check if its being used elsewhere.`
    const modalBodyItem = deleteModel.querySelector('.modal-body p#delete-item')
    modalBodyItem.innerHTML = identifier
  })
}
