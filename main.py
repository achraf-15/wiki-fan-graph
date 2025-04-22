# main.py

from crawler.crawler import crawl
from embedding.embedding_main import embedding_main
from knowledge_graph.build import   build_main

update_only = True # to do: use levels (with or without sub pages)

batch_size = 32
reset_table = True # argument orchestration, reset_table = not(update_only); force_reset_table ( see cli jargon )

top_k = 3
save_to_local=True
from_local=False 

verbose = 2


if __name__ == "__main__":

    
    crawl(
        verbose=verbose,
        update_only=update_only
        )
    
    
    embedding_main(
        batch_size = batch_size, 
        reset_table = reset_table, 
        verbose=verbose
    )

    
    build_main(
        top_k = top_k,
        save_to_local=save_to_local, 
        from_local=from_local, 
        verbose=verbose
    )
    