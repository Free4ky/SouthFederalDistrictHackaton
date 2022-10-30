from src.utils import get_unique_values, get_reverse_rank

import numpy as np
import pickle as pk
from src.wheelchair import RepresentationModel
from sklearn.metrics.pairwise import cosine_similarity


class Predictor:
    def __init__(self, model, industries: dict, techs: dict) -> None:
        self.model = model
        self.industries = industries
        self.techs = techs

    def validate(
        self,
        description: str='',
        industry: str='',
        subindustry: str='',
        tech1: str='',
        tech2: str='',
        tech3: str='',
        threshold: float=0.5,
    ):
        result = {
            'industries': [],
            'subindustries': [],
            'techs1': [],
            'techs2': [],
            'techs3': [],
        }

        # Calculate description embedding
        description_embedding = self.model.encode_sentences(
            [description],
            combine_strategy='mean',
        )

        # Check industry
        industries_similarity = cosine_similarity(description_embedding, self.industries['embedding'])[0]
        industries_top = self.industries['industry'][np.argsort(-industries_similarity)]
        subindustries_top = self.industries['subindustry'][np.argsort(-industries_similarity)]
        
        current_industry_score = get_reverse_rank(get_unique_values(industries_top), industry)
        current_subindustry_score = get_reverse_rank(get_unique_values(subindustries_top), subindustry)

        if current_industry_score < threshold:
            result['industries'] = list(industries_top[:5])
            result['subindustries'] = list(subindustries_top[:5])
        elif current_subindustry_score < threshold:
            result['subindustries'] = list(subindustries_top[industries_top == industry][:5])
        
        # Check technology
        techs_similarity = cosine_similarity(description_embedding, self.techs['embedding'])[0]
        techs1_top = self.techs['tech1'][np.argsort(-techs_similarity)]
        techs2_top = self.techs['tech2'][np.argsort(-techs_similarity)]
        techs3_top = self.techs['tech3'][np.argsort(-techs_similarity)]

        current_tech1_score = get_reverse_rank(get_unique_values(techs1_top), tech1)
        current_tech2_score = get_reverse_rank(get_unique_values(techs2_top), tech2)
        current_tech3_score = get_reverse_rank(get_unique_values(techs3_top), tech3)

        if current_tech1_score < threshold:
            result['techs1'] = list(techs1_top[:5])
            result['techs2'] = list(techs2_top[:5])
            result['techs3'] = list(techs3_top[:5])
        elif current_tech2_score < threshold:
            result['tech2s'] = list(techs2_top[techs1_top == tech1][:5])
            result['tech3s'] = list(techs3_top[techs1_top == tech1][:5])
        elif current_tech3_score < threshold:
            result['tech3s'] = list(techs3_top[techs2_top == tech2][:5])
        
        return result


with open('data/industries.pk', 'rb') as f:
    industries = pk.load(f)
with open('data/techs.pk', 'rb') as f:
    techs = pk.load(f)
model = RepresentationModel(
    model_type='bert',
    model_name='DeepPavlov/rubert-base-cased',
    use_cuda=False,
)
predictor = Predictor(model, industries, techs)
