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
