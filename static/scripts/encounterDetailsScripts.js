let encounterId = $('#encounter-id').data('id')

$(document).ready(function(){
    loadMonsters()
})

async function loadMonsters() {
    let resp = await axios.post(`/encounter/${encounterId}`)
    let monsters = resp.data
    loadingSpinner('#monster-section')
    await getMonsters(monsters)
    endSpinner()
    appendMonsters(monsterTracker)
}

async function getMonsters(monsters) {
    for (let i in monsters) {
        let resp = await axios.get(`https://api.open5e.com/monsters/?name=${i}`)
        let monster = resp.data.results[0]
        monsterTracker[`${monster.slug}`] = {}
        monsterTracker[`${monster.slug}`]['count'] = parseInt(monsters[i])
        monsterTracker[`${monster.slug}`]['name'] = monster.name
        monsterTracker[`${monster.slug}`]['data'] = monster
    }
}

function createUpdateRef(callback){
    let monsterRef = getRef(monsterTracker)
    $('#monsterRef').val(monsterRef)
    callback();
}

function submitUpdate() {
    $('#update-form').submit()
}

function updateHandler() {
    createUpdateRef(submitUpdate)
}

$('#update-btn').on('click', updateHandler)