---
title: "Chat de Whatsapp con +34 647 00 10 54"
type: source
status: NEW
tags:
  - "chat"
  - "whatsapp-chat"
  - "reactjs"
  - "redux"
  - "react-router-dom"
  - "internet"
created: 2026-04-18
updated: 2026-04-18
tokens_consumed: 1429
sources:
  - "/home/marcos/Descargas/Chat de WhatsApp con +34 647 00 10 54.zip"
Summary: "La conversación abarca desde una discusión sobre la cifración en WhatsApp hasta comunicaciones más personales y referencias a sitios web."
requires_verification: true
validated: ~
---

# Chat de Whatsapp con +34 647 00 10 54

> La conversación abarca desde una discusión sobre la cifración en WhatsApp hasta comunicaciones más personales y referencias a sitios web.

## Concepts

- Cifrado en WhatsApp
- React Hooks (useState, useEffect)
- Selectors con redux

## Decisions / Conclusions

- Implementar una función para buscar productos por ID usando el backend.


## Where This Applies

### BJJ RAG Implementation — **HIGH**

The WhatsApp chat summary discusses React Hooks and Selectors with redux, which are relevant to implementing the BJJ-specific Graph Agent (RAG) as it likely requires state management similar to these concepts.

**Action:** Study W: Implement Custom Graph Service without LangGraph in Java/Python for developing a secure contract that integrates seamlessly with bjj-app's architecture, ensuring modularity and security.

### TFG BJJ App — **HIGH**

The technical project summary aligns well with the TFG (Team Framework) for bjj-app, which seems to be concerned with document management and decision-making processes related to system architecture and security protocols.

**Action:** Add to Z: Expand on the index of GEF Management by integrating RAG agentic concepts discussed in WhatsApp chat into TFG's documentation for `bjj-app`, particularly focusing on contract Java/Python.

## Source

- URL: /home/marcos/Descargas/Chat de WhatsApp con +34 647 00 10 54.zip
- Type: chat
- Domain: Tech, Web Development

## Raw Extract (excerpt)

24/10/24, 14:44 - Los mensajes que envías a tu propio número están cifrados de extremo a extremo. Nadie más, ni siquiera WhatsApp, puede leerlos, escucharlos ni compartirlos. Más información
24/10/24, 14:44 - Marcos Arango: <Multimedia omitido>
1/11/24, 14:14 - Marcos Arango: <Multimedia omitido>
1/11/24, 14:14 - Marcos Arango: <Multimedia omitido>
1/11/24, 14:14 - Marcos Arango: <Multimedia omitido>
1/11/24, 14:14 - Marcos Arango: <Multimedia omitido>
1/11/24, 14:14 - Marcos Arango: <Multimedia omitido>
1/11/24, 14:14 - Marcos Arango: <Multimedia omitido>
1/11/24, 14:14 - Marcos Arango: <Multimedia omitido>
1/11/24, 14:14 - Marcos Arango: <Multimedia omitido>
1/11/24, 14:14 - Marcos Arango: <Multimedia omitido>
31/3/25, 21:58 - Marcos Arango: https://www.lavanguardia.com/motor/20230415/8890940/historia-desconocido-lotec-c1000-capricho-multimillonario-jeque-queria-coche-mas-rapido-mundo-1995-pmv.html
30/4/25, 17:10 - Marcos Arango: <Multimedia omitido>
30/4/25, 17:10 - Marcos Arango: <Multimedia omitido>
6/5/25, 14:57 - Marcos Arango: import {useState, useEffect} from 'react';
import {useSelector} from 'react-redux';
import {FormattedMessage, FormattedNumber} from 'react-intl';
import {useParams} from 'react-router-dom';

import * as selectors from '../selectors';
import backend from '../../../backend';
import {BackLink} from '../../common';

const ProductDetails = () => {
    const [product, setProduct] = useState(null);
    const categories = useSelector(selectors.getCategories);
    const {id} = useParams();
    const productId = Number(id);

    useEffect(() => {
        const findProductById = async productId => {
            if (!Number.isNaN(productId)) {
                const response = await backend.productService.findProductById(productId);
                if (response.ok) {
                    setProduct(response.payload);
                }
            }
        };

        findProductById(productId);
    }, [productId]);

    if (!product) {
        retu
