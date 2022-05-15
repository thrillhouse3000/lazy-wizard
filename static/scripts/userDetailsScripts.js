async function deleteEncounter(evt) {
    evt.preventDefault()
    let el  = $(evt.target).parent()
    let id = el.data('id')

    await axios.post(`/encounter/${id}/delete`)
    el.remove()
}

$('#user-encounters').on('submit', '.encounter-delete-form', deleteEncounter)