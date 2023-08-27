function Image(elem)
    elem.attributes.loading = "lazy"
    return elem
end

function Para(elem)
    if string.find(elem.content, "{.*}") then
        elem.attributes.loading = "lazy"
    end
    return elem
end